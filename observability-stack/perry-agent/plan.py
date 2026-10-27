#!/usr/bin/env python3
"""
OIAB Tiered Remediation Planner - classify + plan phase.

Takes a business DIRECTIVE + the enumerated findings, asks Bedrock (Claude) to:
  - classify each finding easy / medium / advanced,
  - confirm/estimate monthly savings,
  - propose a concrete remediation per finding,
  - produce a tiered PROJECT PLAN, and
  - draft a SCOPED-PERMISSION ASK: exactly which easy-tier actions it would
    self-execute if granted autonomy, and what it would hand back as a plan.

This is the capability the director described: directive in -> tiered plan
with savings + "may I self-remediate the easy tier?" out.
"""
import json, sys, os
import boto3
from alert_triage_agent import _extract_json  # reuse robust JSON extraction
import scoring  # DETERMINISTIC tier + priority (no LLM in the scoring path)

REGION = os.environ.get("AWS_REGION","us-east-1")
MODEL  = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Map a raw enumerated finding to the signals scoring.remediation_priority needs.
# Heuristics are deterministic: category + source drive risk/effort/reversibility.
def _score_finding(f):
    cat = str(f.get("category","")).lower()
    # effort/risk/reversibility defaults by category, overridable by explicit fields
    if cat == "waste":
        effort, risk, reversible = "easy", "low", True
    elif cat in ("eol-extended-support", "health"):
        effort, risk, reversible = "advanced", "medium", False
    elif cat == "cost":
        effort, risk, reversible = "medium", "low", True
    else:
        effort, risk, reversible = "medium", "medium", False
    signals = {
        "est_monthly_savings": f.get("est_monthly_savings", 0),
        "effort": f.get("effort", effort),
        "risk": f.get("risk", risk),
        "reversible": f.get("reversible", reversible),
        "source": f.get("source", "live"),
    }
    return scoring.remediation_priority(signals)

PROMPT = """You are an autonomous AWS operations remediation planner. A leader gave you a
business DIRECTIVE and a list of enumerated FINDINGS. Each finding has ALREADY been
assigned a tier and priority by a deterministic scoring engine (the `_tier` and
`_priority` fields). You MUST respect those tiers exactly; do NOT reclassify. Your job
is to write the human-facing action, rationale, savings, and the self-remediation ask.

DIRECTIVE:
{directive}

FINDINGS (JSON; _tier and _priority are authoritative, computed, not yours to change.
source=live means read from the real account now, source=sample is a labeled placeholder):
{findings}

For each finding keep it in the tier given by its `_tier`. Write a concrete `action`.
Respond in STRICT JSON:
{{
  "directive_restated": "one line",
  "total_estimated_monthly_savings": <number>,
  "tiers": {{
    "easy":     [{{"resource":"","action":"","est_monthly_savings":<n>,"reversible":true,"priority":<n>}}],
    "medium":   [{{"resource":"","action":"","est_monthly_savings":<n>,"needs":"","priority":<n>}}],
    "advanced": [{{"resource":"","action":"","est_monthly_savings":<n>,"risk":"","priority":<n>}}]
  }},
  "self_remediation_request": {{
    "summary": "what I am asking permission to do autonomously",
    "scope": "exact resource selector I would act on (e.g. tag Project=oiab-demo only)",
    "easy_actions": ["concrete action 1", "..."],
    "projected_savings_if_approved": <number>,
    "what_i_will_NOT_touch": ["medium/advanced items left as a plan for humans"]
  }},
  "operator_oneliner": "the blunt 'here is the deal' summary a leader would want"
}}"""

def make_plan(directive, findings):
    # 1) DETERMINISTIC pass: compute tier + priority for every finding first.
    scored = []
    for f in (findings or []):
        s = _score_finding(f)
        g = dict(f); g["_tier"] = s["tier"]; g["_priority"] = s["priority_score"]; g["_safety"] = s["safety"]
        scored.append(g)
    # 2) LLM pass: prose only, told the tiers are fixed.
    agent_bedrock = boto3.client("bedrock-runtime", region_name=REGION)
    prompt = PROMPT.format(directive=directive, findings=json.dumps(scored)[:9000])
    resp = agent_bedrock.invoke_model(modelId=MODEL,
        body=json.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":2000,
                          "messages":[{"role":"user","content":prompt}]}))
    text = json.loads(resp["body"].read())["content"][0]["text"]
    plan = _extract_json(text)
    # 3) ENFORCE determinism: rebuild tiers from computed scores, keep LLM's action text
    #    by matching on resource. The scoring engine, not the LLM, owns the tiering.
    try:
        llm_actions = {}
        for tier in ("easy","medium","advanced"):
            for item in plan.get("tiers",{}).get(tier,[]):
                if isinstance(item, dict) and item.get("resource"):
                    llm_actions[item["resource"]] = item.get("action","")
        rebuilt = {"easy": [], "medium": [], "advanced": []}
        total = 0.0
        for g in sorted(scored, key=lambda x: -scoring._num(x.get("_priority"))):
            res = g.get("resource","")
            total += scoring._num(g.get("est_monthly_savings"))
            rebuilt[g["_tier"]].append({
                "resource": res,
                "action": llm_actions.get(res, f"Remediate {res}"),
                "est_monthly_savings": scoring._num(g.get("est_monthly_savings")),
                "priority": g["_priority"],
                "source": g.get("source","live"),
            })
        plan["tiers"] = rebuilt
        plan["total_estimated_monthly_savings"] = round(total, 2)
        plan["_scoring"] = "deterministic (scoring.py); tiers computed, not LLM-assigned"
    except Exception as e:
        plan["_scoring_error"] = str(e)
    return plan

if __name__ == "__main__":
    directive = os.environ.get("DIRECTIVE") or (" ".join(sys.argv[1:]) or
        "Build me a remediation plan for my extended-support exposure and future cost. "
        "Tier it easy/medium/advanced with savings, and tell me what you can safely fix yourself.")
    findings = json.load(open("/tmp/findings.json")) if os.path.exists("/tmp/findings.json") else []
    plan = make_plan(directive, findings)
    print("="*80)
    print("DIRECTIVE:", plan.get("directive_restated"))
    print(f"TOTAL EST. SAVINGS: ${plan.get('total_estimated_monthly_savings')}/mo")
    for tier in ("easy","medium","advanced"):
        items = plan.get("tiers",{}).get(tier,[])
        print(f"\n--- {tier.upper()} ({len(items)}) ---")
        for it in items:
            print(f"  {it.get('resource','')}: {it.get('action','')}  ~${it.get('est_monthly_savings',0)}/mo")
    r = plan.get("self_remediation_request",{})
    print("\n=== SCOPED AUTONOMY REQUEST ===")
    print("  Ask    :", r.get("summary"))
    print("  Scope  :", r.get("scope"))
    print("  Would do:", "; ".join(r.get("easy_actions",[])))
    print("  Savings :", f"${r.get('projected_savings_if_approved')}/mo if approved")
    print("  Won't touch:", "; ".join(r.get("what_i_will_NOT_touch",[])))
    print("\nONE-LINER:", plan.get("operator_oneliner"))
    print("="*80)
    json.dump(plan, open("/tmp/plan.json","w"))
