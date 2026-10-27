#!/usr/bin/env python3
"""
OIAB deterministic signal scoring.

Pure, deterministic, fail-closed scoring. NO LLM in this path, no randomness,
no wall-clock dependence. Same inputs -> same score, every time. Every public
function guards against None / NaN / inf / negative / wrong-type / div-by-zero
and returns a bounded, sane result instead of raising.

Two scores:
  operational_severity(factors)  -> 0..100 + bucket (critical/high/medium/low)
      from magnitude, duration, baseline deviation (z), blast radius, trend,
      off-schedule flag. This is "how bad is this fleet signal right now".
  remediation_priority(finding)  -> 0..100 + computed tier (easy/medium/advanced)
      from monthly savings, effort, risk, reversibility, source confidence.
      This REPLACES LLM tier-guessing with auditable math.

Weights/bounds/thresholds come from scoring-config.yml (tunable, versioned).
If the config is missing or unreadable, built-in DEFAULTS are used (fail-closed,
never crash).
"""
from __future__ import annotations
import math
import os

try:
    import yaml  # optional; defaults used if unavailable
except Exception:  # pragma: no cover
    yaml = None

# ----------------------------------------------------------------------------
# Built-in defaults (used if config missing). Weights within each score sum ~1.
# ----------------------------------------------------------------------------
DEFAULTS = {
    "operational": {
        "weights": {
            "magnitude": 0.30,
            "duration": 0.15,
            "deviation": 0.25,
            "blast_radius": 0.15,
            "trend": 0.10,
            "off_schedule": 0.05,
        },
        "norm": {
            # value at/above which a factor is considered "fully bad" (-> 1.0)
            "magnitude_full_pct": 100.0,     # % utilization
            "baseline_pct": 60.0,            # expected normal utilization
            "duration_full_sec": 900.0,      # 15 min sustained = full
            "deviation_full_z": 4.0,         # z=4 sigma = full
            "blast_full_count": 3.0,         # N nodes affected = full
            "trend_full_slope": 2.0,         # % per minute rising = full
        },
        "buckets": {  # lower-bound score -> label, checked high to low
            "critical": 80,
            "high": 60,
            "medium": 35,
            "low": 0,
        },
    },
    "remediation": {
        "weights": {
            "savings": 0.45,
            "effort": 0.25,
            "risk": 0.15,
            "reversibility": 0.10,
            "confidence": 0.05,
        },
        "norm": {
            "savings_full_usd": 500.0,       # $/mo at which savings factor -> 1
        },
        "effort_score": {                    # higher = easier = higher priority
            "easy": 1.0, "medium": 0.5, "advanced": 0.2,
        },
        "risk_score": {                      # higher = safer = higher priority
            "low": 1.0, "medium": 0.5, "high": 0.2,
        },
        "confidence_score": {
            "live": 1.0, "sample": 0.5,
        },
        # Deterministic tier assignment from effort+risk+reversibility (NOT the LLM).
        "tier_rules": {
            "easy_min": 0.75,     # combined safety score >= -> easy
            "medium_min": 0.45,   # >= -> medium, else advanced
        },
    },
}


# ----------------------------------------------------------------------------
# Safety primitives
# ----------------------------------------------------------------------------
def _num(x, default=0.0):
    """Coerce anything to a finite float. None/NaN/inf/str-garbage -> default."""
    try:
        if x is None:
            return float(default)
        if isinstance(x, bool):
            return 1.0 if x else 0.0
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return float(default)
        return v
    except (TypeError, ValueError):
        return float(default)


def _clamp01(x):
    v = _num(x, 0.0)
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _safe_div(n, d, default=0.0):
    n = _num(n, 0.0)
    d = _num(d, 0.0)
    if d == 0.0:
        return float(default)
    return n / d


def load_config(path=None):
    """Load scoring-config.yml; fall back to DEFAULTS on any problem. Never raises."""
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "scoring-config.yml")
    if yaml is None or not os.path.exists(path):
        return DEFAULTS
    try:
        with open(path) as f:
            cfg = yaml.safe_load(f) or {}
        # shallow-merge over defaults so a partial/garbage config can't break scoring
        merged = {k: dict(v) if isinstance(v, dict) else v for k, v in DEFAULTS.items()}
        for section in ("operational", "remediation"):
            if isinstance(cfg.get(section), dict):
                merged[section] = _deep_merge(DEFAULTS[section], cfg[section])
        return merged
    except Exception:
        return DEFAULTS


def _deep_merge(base, over):
    out = {}
    for k, v in base.items():
        if isinstance(v, dict) and isinstance(over.get(k), dict):
            out[k] = _deep_merge(v, over[k])
        else:
            out[k] = over.get(k, v) if isinstance(over, dict) else v
    for k, v in (over or {}).items():
        if k not in out:
            out[k] = v
    return out


def _weighted(factors: dict, weights: dict):
    """Sum factor(0..1) * weight, renormalized by the weights actually present.
    Missing/garbage factors contribute 0 but are excluded from the weight
    denominator so the score stays on a 0..1 scale (fail-closed, no inflation)."""
    num = 0.0
    wsum = 0.0
    breakdown = {}
    for name, w in weights.items():
        w = _num(w, 0.0)
        if w <= 0:
            continue
        f = _clamp01(factors.get(name))
        num += f * w
        wsum += w
        breakdown[name] = round(f, 4)
    score01 = _safe_div(num, wsum, 0.0)
    return _clamp01(score01), breakdown


def _bucket(score, buckets: dict):
    # check labels by descending lower-bound
    try:
        ordered = sorted(buckets.items(), key=lambda kv: _num(kv[1], 0), reverse=True)
    except Exception:
        ordered = [("low", 0)]
    for label, lb in ordered:
        if score >= _num(lb, 0):
            return label
    return ordered[-1][0] if ordered else "low"


# ----------------------------------------------------------------------------
# 1) Operational severity score
# ----------------------------------------------------------------------------
def operational_factors(raw: dict, cfg=None):
    """Normalize raw operational inputs to 0..1 factors. Pure + fail-closed.

    raw keys (all optional, missing -> 0 contribution):
      value_pct        current utilization %
      baseline_pct     expected normal %   (defaults to config baseline)
      duration_sec     seconds the condition has persisted
      deviation_z      z-score vs learned baseline band
      blast_count      number of nodes affected
      trend_slope      % per minute (positive = worsening)
      off_schedule     bool: True if OUTSIDE a known benign window
    """
    cfg = cfg or load_config()
    n = cfg["operational"]["norm"]

    value = _num(raw.get("value_pct"), 0.0)
    baseline = _num(raw.get("baseline_pct"), n["baseline_pct"])
    full_mag = _num(n["magnitude_full_pct"], 100.0)
    # magnitude: how far above baseline toward "full bad", 0..1
    span = max(full_mag - baseline, 1e-6)
    magnitude = _clamp01(_safe_div(value - baseline, span, 0.0))

    duration = _clamp01(_safe_div(raw.get("duration_sec"), n["duration_full_sec"], 0.0))
    deviation = _clamp01(_safe_div(abs(_num(raw.get("deviation_z"), 0.0)), n["deviation_full_z"], 0.0))
    blast = _clamp01(_safe_div(raw.get("blast_count"), n["blast_full_count"], 0.0))
    # trend only counts when worsening (positive slope)
    slope = _num(raw.get("trend_slope"), 0.0)
    trend = _clamp01(_safe_div(slope, n["trend_full_slope"], 0.0)) if slope > 0 else 0.0
    off = 1.0 if bool(raw.get("off_schedule", False)) else 0.0

    return {
        "magnitude": magnitude,
        "duration": duration,
        "deviation": deviation,
        "blast_radius": blast,
        "trend": trend,
        "off_schedule": off,
    }


def operational_severity(raw: dict, cfg=None):
    """-> dict(score 0..100, bucket, factors). Deterministic, never raises."""
    cfg = cfg or load_config()
    factors = operational_factors(raw, cfg)
    score01, breakdown = _weighted(factors, cfg["operational"]["weights"])
    score = round(score01 * 100.0, 2)
    return {
        "score": score,
        "bucket": _bucket(score, cfg["operational"]["buckets"]),
        "factors": breakdown,
    }


# ----------------------------------------------------------------------------
# 2) Remediation priority score + deterministic tier
# ----------------------------------------------------------------------------
def remediation_priority(finding: dict, cfg=None):
    """Score a remediation finding 0..100 and compute its tier deterministically.

    finding keys:
      est_monthly_savings  USD/mo (number)
      effort               'easy'|'medium'|'advanced'  (optional hint)
      risk                 'low'|'medium'|'high'
      reversible           bool
      source               'live'|'sample'
    Tier is COMPUTED from safety (effort+risk+reversibility), not taken from the
    LLM. Priority blends savings with the safety/confidence factors.
    """
    cfg = cfg or load_config()
    r = cfg["remediation"]

    savings = _clamp01(_safe_div(finding.get("est_monthly_savings"), r["norm"]["savings_full_usd"], 0.0))
    effort = _clamp01(r["effort_score"].get(str(finding.get("effort", "")).lower(), 0.5))
    risk = _clamp01(r["risk_score"].get(str(finding.get("risk", "")).lower(), 0.5))
    reversibility = 1.0 if bool(finding.get("reversible", False)) else 0.3
    confidence = _clamp01(r["confidence_score"].get(str(finding.get("source", "")).lower(), 0.5))

    factors = {
        "savings": savings,
        "effort": effort,
        "risk": risk,
        "reversibility": reversibility,
        "confidence": confidence,
    }
    score01, breakdown = _weighted(factors, r["weights"])
    score = round(score01 * 100.0, 2)

    # Deterministic tier from a safety composite (effort + risk + reversibility).
    safety = (effort + risk + reversibility) / 3.0
    if safety >= _num(r["tier_rules"]["easy_min"], 0.75):
        tier = "easy"
    elif safety >= _num(r["tier_rules"]["medium_min"], 0.45):
        tier = "medium"
    else:
        tier = "advanced"

    return {
        "priority_score": score,
        "tier": tier,
        "safety": round(safety, 4),
        "factors": breakdown,
    }


if __name__ == "__main__":
    # tiny smoke demo
    import json
    print("operational (sustained off-schedule CPU pin):")
    print(json.dumps(operational_severity(
        {"value_pct": 96, "baseline_pct": 10, "duration_sec": 720,
         "deviation_z": 5.0, "blast_count": 3, "trend_slope": 1.2, "off_schedule": True}), indent=2))
    print("operational (benign :05 bump):")
    print(json.dumps(operational_severity(
        {"value_pct": 40, "baseline_pct": 10, "duration_sec": 90,
         "deviation_z": 1.0, "blast_count": 1, "trend_slope": 0.0, "off_schedule": False}), indent=2))
    print("remediation (orphan volume):")
    print(json.dumps(remediation_priority(
        {"est_monthly_savings": 1.5, "risk": "low", "reversible": True, "source": "live"}), indent=2))
    print("remediation (RDS extended support):")
    print(json.dumps(remediation_priority(
        {"est_monthly_savings": 220, "risk": "medium", "reversible": False, "source": "sample"}), indent=2))
