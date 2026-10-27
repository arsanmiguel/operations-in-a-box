# Tiered Remediation Planner - live PoC capture (2026-10-15)

**What this is:** the capability the director described back to us, built and proven live against the work Isengard account (442056872435). An agent that takes a business directive, enumerates issues from real account signals, tiers them easy/medium/advanced with dollar savings, asks for scoped permission, and self-remediates the easy tier reversibly, leaving a project plan for the rest.

**Honesty note (the credible part):** every finding is labeled `source=live` (read from the real account now) or `source=sample` (a clearly-marked enterprise fixture used only where this sandbox cannot provide the signal, i.e. AWS Health, which needs a Business+ support plan). Same code lights up with full live data in a supported account, zero changes.

---

## The workflow, proven end to end

**1. Directive in:**
> "Build me a remediation plan for all my extended support and future costs. Integrate AWS Health, tier these easy/medium/advanced with savings, and tell me what you can go remediate yourself if I grant permission, and how much it would save."

**2. Enumerate (live signals):** Cost Explorer spend/forecast, EC2/EBS inventory, EOL-by-AMI-age, idle/orphaned/unattached waste. Health via live API when supported, else labeled sample.

**3. Tiered plan + savings (Bedrock Claude). Total: ~$401.50/mo**

| Tier | Resource | Action | Savings |
|------|----------|--------|---------|
| EASY | stopped EC2 instance (found live) | snapshot + terminate + delete orphaned EBS | ~$1.50/mo |
| MEDIUM | rds:prod-mysql-1 (sample) | upgrade MySQL 5.7 → 8.0, replica test, cutover window | ~$220/mo |
| ADVANCED | eks:prod-cluster (sample) | upgrade EKS 1.27 → standard-support, validate workloads | ~$180/mo |

**4. Scoped-autonomy ask (the goldmine moment):**
> "I request permission to terminate the stopped instance... here's exactly what I'd do: snapshot for audit, detach, terminate, delete, log to CloudTrail. Scope: that instance only. ~$1.50/mo if approved. I will NOT touch the RDS or EKS items - those are reserved for your platform team."

**5. Self-remediation (executed live, safely):**
- Target: a throwaway `Project=oiab-demo` unattached volume (`vol-00cbd969e13cd14bf`) created as a safe stand-in so we never touch resources we don't own.
- Action: snapshot `snap-09b916405578c8e96` (audit) → delete volume. Reversible.
- Gated by `APPROVE=yes EXECUTE=yes`; IAM condition `aws:ResourceTag/Project=oiab-demo` means it physically cannot delete anything else.

---

## Safety design (why it's trustworthy, not reckless)
- **Hard scope:** executor re-verifies the `Project=oiab-demo` tag at execution time; refuses anything else even if the plan named it. It deliberately did NOT touch the real pre-existing stopped instance it discovered (`i-0c9f9f87f93e028f6`) - that is not ours.
- **Approval gate:** no action without explicit `APPROVE=yes`.
- **Reversible-first:** snapshot before any delete.
- **Least privilege:** the role has read-everything, but delete-volume is tag-conditioned; it earned write access one scoped action at a time.

## Where it lives
- demo-host `i-00dde6bce92365450`, `/opt/planner/` : `remediation_planner.py` (enumerate), `plan.py` (Bedrock tier+savings+ask), `execute_easy.py` (scoped gated executor).
- IAM: `oiab-planner-read` (CE/Health/inventory), `oiab-easytier-exec` (scoped snapshot+delete).

## The gap to close for the real follow-up
- Enable AWS Health on the account (or run in a Business+ account) → the two `sample` RDS/EKS findings become `live`, and the $400/mo becomes a real number from the real environment.
- Everything else already runs on live data.
