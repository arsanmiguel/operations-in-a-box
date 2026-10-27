#!/usr/bin/env python3
"""
Tests for scoring.py: determinism + bounds + fail-closed robustness.
Plain asserts (no pytest dependency). Run: python3 test_scoring.py
Exit 0 = all pass.
"""
import math
import scoring as s

PASS = 0
FAIL = 0

def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name}")

# ---- determinism: same input -> identical output, repeatedly ----
raw = {"value_pct": 96, "baseline_pct": 10, "duration_sec": 720,
       "deviation_z": 5.0, "blast_count": 3, "trend_slope": 1.2, "off_schedule": True}
r1 = s.operational_severity(raw)
r2 = s.operational_severity(dict(raw))
r3 = s.operational_severity(dict(raw))
check("operational deterministic", r1 == r2 == r3)

fnd = {"est_monthly_savings": 220, "risk": "medium", "reversible": False, "source": "sample"}
p1 = s.remediation_priority(fnd)
p2 = s.remediation_priority(dict(fnd))
check("remediation deterministic", p1 == p2)

# ---- bounds: score always 0..100 ----
check("op score in range", 0 <= r1["score"] <= 100)
check("rem score in range", 0 <= p1["priority_score"] <= 100)

# ---- ordering sanity: bad signal scores higher than benign ----
benign = s.operational_severity({"value_pct": 40, "baseline_pct": 10, "duration_sec": 90,
                                 "deviation_z": 1.0, "blast_count": 1, "trend_slope": 0.0,
                                 "off_schedule": False})
check("bad > benign", r1["score"] > benign["score"])
check("bad bucket critical/high", r1["bucket"] in ("critical", "high"))
check("benign bucket low/medium", benign["bucket"] in ("low", "medium"))

# ---- tier computed deterministically, not from LLM ----
easy = s.remediation_priority({"est_monthly_savings": 1.5, "risk": "low", "reversible": True, "source": "live"})
adv = s.remediation_priority({"est_monthly_savings": 180, "risk": "high", "reversible": False, "source": "sample"})
check("easy tier", easy["tier"] == "easy")
check("advanced tier", adv["tier"] == "advanced")

# ---- FAIL-CLOSED torture: garbage must never raise, must stay bounded ----
garbage_inputs = [
    None, {}, {"value_pct": None}, {"value_pct": "lol"}, {"value_pct": float("nan")},
    {"value_pct": float("inf")}, {"value_pct": -999}, {"value_pct": 1e18},
    {"duration_sec": -5, "blast_count": "x", "deviation_z": None, "trend_slope": "NaN"},
    {"value_pct": [1,2,3]}, {"value_pct": {"a": 1}}, {"off_schedule": "yes"},
]
for i, g in enumerate(garbage_inputs):
    try:
        out = s.operational_severity(g if isinstance(g, dict) else (g or {}))
        ok = (0 <= out["score"] <= 100) and out["bucket"] in ("critical","high","medium","low")
        check(f"op garbage[{i}] bounded+no-raise", ok)
    except Exception as e:
        check(f"op garbage[{i}] no-raise (raised {type(e).__name__})", False)

rem_garbage = [
    None, {}, {"est_monthly_savings": None}, {"est_monthly_savings": "free"},
    {"est_monthly_savings": float("nan")}, {"est_monthly_savings": -5},
    {"risk": 123, "effort": None, "source": object()}, {"reversible": "maybe"},
    {"est_monthly_savings": float("inf")},
]
for i, g in enumerate(rem_garbage):
    try:
        out = s.remediation_priority(g if isinstance(g, dict) else (g or {}))
        ok = (0 <= out["priority_score"] <= 100) and out["tier"] in ("easy","medium","advanced")
        check(f"rem garbage[{i}] bounded+no-raise", ok)
    except Exception as e:
        check(f"rem garbage[{i}] no-raise (raised {type(e).__name__})", False)

# ---- config robustness: missing/garbage config path -> defaults, no raise ----
try:
    cfg = s.load_config("/nonexistent/path/nope.yml")
    check("missing config -> defaults", isinstance(cfg, dict) and "operational" in cfg)
except Exception:
    check("missing config no-raise", False)

# ---- safe primitives ----
check("_num None", s._num(None) == 0.0)
check("_num nan", s._num(float("nan")) == 0.0)
check("_num str", s._num("1.5") == 1.5)
check("_clamp01 over", s._clamp01(5) == 1.0)
check("_clamp01 under", s._clamp01(-5) == 0.0)
check("_safe_div zero", s._safe_div(1, 0) == 0.0)

print(f"\n{PASS} passed, {FAIL} failed")
raise SystemExit(1 if FAIL else 0)
