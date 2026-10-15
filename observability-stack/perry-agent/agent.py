#!/usr/bin/env python3
"""
Perry the Agent (placeholder name) - unified operator agent entrypoint.

Two capabilities behind one CLI:
  agent.py diagnose "<symptom>"   -> context-aware root-cause + fix (from diagnose.py)
  agent.py plan "<directive>"     -> enumerate + tiered remediation plan + savings
                                      + scoped-autonomy ask (remediation_planner.py + plan.py),
                                      and PUSHES savings metrics to Pushgateway for Grafana,
                                      and writes the latest plan JSON for the web page.

Shared Bedrock path via alert_triage_agent. Keeps the demo's "one agent, native,
context-aware" story: it reports OR acts, and now it's visible in the browser.
"""
import sys, os, json, datetime, urllib.request
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PUSHGATEWAY = os.environ.get("PUSHGATEWAY_URL", "http://pushgateway:9091")
PLAN_JSON = "/opt/planner/latest_plan.json"

def _push_savings(plan):
    """Push tiered savings + finding counts to Pushgateway (Prometheus scrapes it)."""
    tiers = plan.get("tiers", {})
    total = float(plan.get("total_estimated_monthly_savings", 0) or 0)
    lines = [
        '# TYPE oiab_remediation_savings_usd_total gauge',
        f'oiab_remediation_savings_usd_total {total}',
        '# TYPE oiab_remediation_savings_usd gauge',
    ]
    for tier in ("easy","medium","advanced"):
        s = sum(float(i.get("est_monthly_savings",0) or 0) for i in tiers.get(tier,[]))
        lines.append(f'oiab_remediation_savings_usd{{tier="{tier}"}} {s}')
    lines.append('# TYPE oiab_remediation_findings gauge')
    for tier in ("easy","medium","advanced"):
        lines.append(f'oiab_remediation_findings{{tier="{tier}"}} {len(tiers.get(tier,[]))}')
    body = ("\n".join(lines) + "\n").encode()
    req = urllib.request.Request(f"{PUSHGATEWAY}/metrics/job/remediation-planner",
                                 data=body, method="POST")
    try:
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception as e:
        print("push failed:", e); return False

def do_plan(directive):
    rp = importlib.import_module("remediation_planner")
    planmod = importlib.import_module("plan")
    findings = rp.enumerate_findings()
    json.dump(findings, open("/tmp/findings.json","w"))
    plan = planmod.make_plan(directive, findings)
    plan["_generated_at"] = datetime.datetime.utcnow().isoformat()+"Z"
    plan["_findings"] = findings
    json.dump(plan, open(PLAN_JSON,"w"))
    pushed = _push_savings(plan)
    print(f"Plan generated. Total savings ${plan.get('total_estimated_monthly_savings')}/mo. "
          f"Metrics pushed: {pushed}. Plan written: {PLAN_JSON}")
    print(plan.get("operator_oneliner",""))
    return plan

def do_diagnose(symptom):
    dmod = importlib.import_module("diagnose")
    result, ctx = dmod.diagnose(symptom)
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("diagnose","plan"):
        print("usage: agent.py {diagnose <symptom> | plan <directive>}"); sys.exit(1)
    mode = sys.argv[1]; arg = " ".join(sys.argv[2:])
    if mode == "plan":
        do_plan(arg or "Build a tiered remediation plan for extended support and cost, with savings and a scoped autonomy ask.")
    else:
        do_diagnose(arg or "a fleet node shows up=0 and is not being scraped")
