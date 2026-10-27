#!/usr/bin/env python3
"""
OIAB signal-score collector.

Queries Prometheus for the operational factors per fleet node, runs the
DETERMINISTIC scoring.operational_severity() over them, and pushes
oiab_signal_score{instance,bucket} plus per-factor gauges to Pushgateway so
Grafana can show a live, explainable Signal Score. No LLM in this path.

Baseline note: the ":05 scheduled bulk load" is a known benign window. If the
current minute is within the off_window, off_schedule=False (expected); any
sustained spike outside it flags off_schedule=True and scores higher.
"""
import json, os, urllib.request, urllib.parse, datetime
import scoring

PROM = os.environ.get("PROM_URL", "http://localhost:9090")
PUSHGATEWAY = os.environ.get("PUSHGATEWAY_URL", "http://localhost:9091")
OFF_WINDOW_MIN = 5          # the benign :05 bulk-load minute
BASELINE_PCT = 10.0         # learned quiet baseline for this fleet

def _q(expr):
    """Prometheus instant query -> list of (labels, value). Fail-closed to []."""
    try:
        url = f"{PROM}/api/v1/query?query=" + urllib.parse.quote(expr)
        with urllib.request.urlopen(url, timeout=6) as r:
            d = json.load(r)
        out = []
        for res in d.get("data", {}).get("result", []):
            out.append((res.get("metric", {}), res.get("value", [None, None])[1]))
        return out
    except Exception:
        return []

def collect():
    # current CPU utilization % per fleet node (5m avg)
    cpu = _q('100-(avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m]))*100)')
    # how long (approx) above a threshold: fraction of last 15m spent >50% util, scaled to seconds
    dur = dict((m.get("instance"), v) for m, v in _q(
        'sum_over_time((100-(avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[2m]))*100) > bool 50)[15m:1m])*60'))
    # trend: linear prediction slope of util over next 10m (approx %/min)
    trend = dict((m.get("instance"), v) for m, v in _q(
        'predict_linear((100-(avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m]))*100))[10m:1m], 60) '
        '- (100-(avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m]))*100))'))

    # blast radius: how many fleet nodes currently above 70%
    hot = _q('count((100-(avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m]))*100)) > 70)')
    blast = scoring._num(hot[0][1], 0.0) if hot else 0.0

    now_min = datetime.datetime.utcnow().minute
    off_schedule = not (now_min in (OFF_WINDOW_MIN, OFF_WINDOW_MIN+1, OFF_WINDOW_MIN+2, OFF_WINDOW_MIN+3))

    lines = ['# TYPE oiab_signal_score gauge']
    factor_lines = ['# TYPE oiab_signal_factor gauge']
    results = []
    for metric, val in cpu:
        inst = metric.get("instance", "unknown")
        value_pct = scoring._num(val, 0.0)
        # z-score deviation vs baseline using a rough fleet sigma of 15 (deterministic, config-free here)
        dev_z = abs(value_pct - BASELINE_PCT) / 15.0
        raw = {
            "value_pct": value_pct,
            "baseline_pct": BASELINE_PCT,
            "duration_sec": scoring._num(dur.get(inst), 0.0),
            "deviation_z": dev_z,
            "blast_count": blast,
            "trend_slope": scoring._num(trend.get(inst), 0.0),
            # only "off schedule" matters when the signal is actually elevated
            "off_schedule": off_schedule and value_pct > (BASELINE_PCT * 2),
        }
        sev = scoring.operational_severity(raw)
        safe_inst = inst.replace('"', '')
        lines.append(f'oiab_signal_score{{instance="{safe_inst}",bucket="{sev["bucket"]}"}} {sev["score"]}')
        for fname, fval in sev["factors"].items():
            factor_lines.append(f'oiab_signal_factor{{instance="{safe_inst}",factor="{fname}"}} {fval}')
        results.append((inst, sev))

    body = ("\n".join(lines + factor_lines) + "\n").encode()
    try:
        req = urllib.request.Request(f"{PUSHGATEWAY}/metrics/job/signal-scoring", data=body, method="POST")
        urllib.request.urlopen(req, timeout=5)
        pushed = True
    except Exception as e:
        pushed = False
        print("push failed:", e)
    for inst, sev in results:
        print(f"  {inst:22} score={sev['score']:6}  bucket={sev['bucket']}")
    print(f"pushed={pushed} ({len(results)} nodes)")
    return results

if __name__ == "__main__":
    collect()
