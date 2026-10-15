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

REGION = os.environ.get("AWS_REGION","us-east-1")
MODEL  = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

PROMPT = """You are an autonomous AWS operations remediation planner. A leader gave you a
business DIRECTIVE and a list of enumerated FINDINGS from their account. Produce a
tiered remediation plan the way a senior SRE/FinOps engineer would, honest about what
is a safe self-service fix versus what needs human design.

DIRECTIVE:
{directive}

FINDINGS (JSON; source=live means read from the real account now, source=sample means a
labeled placeholder for a signal this sandbox account cannot provide):
{findings}

Classify EACH finding into exactly one tier:
- "easy": safe, reversible, low-blast-radius, automatable now (e.g. delete unattached
  volume, stop/terminate idle resource, add missing tag). Candidate for self-remediation.
- "medium": needs a change window or light coordination (e.g. rightsizing, snapshot+rebuild).
- "advanced": needs design/validation or carries real risk (e.g. engine major-version upgrade
  to exit extended support, cross-service migration).

Respond in STRICT JSON:
{{
  "directive_restated": "one line",
  "total_estimated_monthly_savings": <number>,
  "tiers": {{
    "easy":     [{{"resource":"","action":"","est_monthly_savings":<n>,"reversible":true}}],
    "medium":   [{{"resource":"","action":"","est_monthly_savings":<n>,"needs":""}}],
    "advanced": [{{"resource":"","action":"","est_monthly_savings":<n>,"risk":""}}]
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
    agent_bedrock = boto3.client("bedrock-runtime", region_name=REGION)
    prompt = PROMPT.format(directive=directive, findings=json.dumps(findings)[:9000])
    resp = agent_bedrock.invoke_model(modelId=MODEL,
        body=json.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":2000,
                          "messages":[{"role":"user","content":prompt}]}))
    text = json.loads(resp["body"].read())["content"][0]["text"]
    return _extract_json(text)

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
