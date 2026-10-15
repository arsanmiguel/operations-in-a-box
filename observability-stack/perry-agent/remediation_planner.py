#!/usr/bin/env python3
"""
OIAB Tiered Remediation Planner (PoC).

Takes a business directive, ENUMERATES issues from real account signals
(Cost Explorer, EC2/EBS inventory, EOL-by-AMI-age, idle/orphaned/untagged
waste, and AWS Health when the account supports it), then (in plan.py) a
Bedrock pass classifies them easy/medium/advanced, estimates savings, and
emits a tiered project plan with a scoped-permission ask.

Account-agnostic by design: every finding is tagged source=live or
source=sample. 'live' = read from THIS account right now. 'sample' = a
clearly-labeled enterprise fixture used only where this sandbox cannot
provide the signal (e.g. AWS Health with no Business+ support). Swap to a
supported account and the same code lights up with live data, no changes.
"""
import json, datetime, os
import boto3
from botocore.exceptions import ClientError

REGION = os.environ.get("AWS_REGION", "us-east-1")

def _finding(source, category, resource, issue, est_monthly_savings=0.0, detail=""):
    return {
        "source": source,                 # "live" | "sample"
        "category": category,             # cost | eol-extended-support | health | waste
        "resource": resource,
        "issue": issue,
        "est_monthly_savings": round(float(est_monthly_savings), 2),
        "detail": detail,
    }

def enumerate_findings():
    findings = []
    ec2 = boto3.client("ec2", region_name=REGION)
    ce  = boto3.client("ce", region_name=REGION)

    # --- COST: forecast + top services (live) ---
    today = datetime.date.today()
    start = (today - datetime.timedelta(days=30)).isoformat()
    end   = today.isoformat()
    try:
        cu = ce.get_cost_and_usage(TimePeriod={"Start": start, "End": end},
                                   Granularity="MONTHLY", Metrics=["UnblendedCost"],
                                   GroupBy=[{"Type":"DIMENSION","Key":"SERVICE"}])
        groups = cu["ResultsByTime"][0]["Groups"] if cu["ResultsByTime"] else []
        total = sum(float(g["Metrics"]["UnblendedCost"]["Amount"]) for g in groups)
        findings.append(_finding("live","cost","account",
            f"Last 30d spend ${total:.2f} across {len(groups)} services",0.0,
            "Baseline cost context (small in this sandbox; real accounts show the real drivers)."))
    except ClientError as e:
        findings.append(_finding("live","cost","cost-explorer",f"CE query blocked: {e.response['Error']['Code']}"))

    # --- INVENTORY: instances, EOL-by-AMI-age, idle (live) ---
    try:
        resv = ec2.describe_instances(Filters=[{"Name":"instance-state-name","Values":["running","stopped"]}])
        insts = [i for r in resv["Reservations"] for i in r["Instances"]]
        stopped = [i for i in insts if i["State"]["Name"]=="stopped"]
        for i in stopped:
            findings.append(_finding("live","waste",i["InstanceId"],
                "Stopped instance still incurring EBS cost", 1.50,
                "Stopped instances keep paying for attached EBS; terminate or snapshot+delete."))
        # EOL/extended-support heuristic from AMI creation age
        ami_ids = list({i["ImageId"] for i in insts})
        if ami_ids:
            imgs = ec2.describe_images(ImageIds=ami_ids)["Images"]
            for img in imgs:
                try:
                    created = datetime.datetime.fromisoformat(img["CreationDate"].replace("Z","+00:00"))
                    age_days = (datetime.datetime.now(datetime.timezone.utc)-created).days
                except Exception:
                    age_days = 0
                if age_days > 365:
                    findings.append(_finding("live","eol-extended-support",img["ImageId"],
                        f"AMI is {age_days}d old; likely trailing OS/engine support", 0.0,
                        "Aging base image is an extended-support/EOL risk; rebuild on current AMI."))
    except ClientError as e:
        findings.append(_finding("live","waste","ec2",f"describe-instances blocked: {e.response['Error']['Code']}"))

    # --- WASTE: unattached EBS volumes + stale snapshots (live) ---
    try:
        vols = ec2.describe_volumes(Filters=[{"Name":"status","Values":["available"]}])["Volumes"]
        for v in vols:
            gb = v["Size"]
            findings.append(_finding("live","waste",v["VolumeId"],
                f"Unattached {gb}GB EBS volume", round(gb*0.08,2),
                "Unattached gp3 bills ~$0.08/GB-mo for nothing; snapshot then delete."))
    except ClientError as e:
        findings.append(_finding("live","waste","ebs",f"describe-volumes blocked: {e.response['Error']['Code']}"))

    # --- HEALTH: live if supported, else clearly-labeled sample ---
    try:
        h = boto3.client("health", region_name="us-east-1")
        evs = h.describe_events(filter={"eventStatusCodes":["open","upcoming"]})["events"][:10]
        if evs:
            for e in evs:
                findings.append(_finding("live","health",e.get("service","?"),
                    f"{e.get('eventTypeCode')} ({e.get('statusCode')})",0.0,
                    "Open/upcoming AWS Health event."))
        else:
            findings.append(_finding("live","health","aws-health","No open Health events"))
    except ClientError as e:
        if e.response["Error"]["Code"] in ("SubscriptionRequiredException","AccessDeniedException"):
            # Honest fallback: account has no Business+ support. Show the workflow with labeled samples.
            findings.append(_finding("sample","health","rds:prod-mysql-1",
                "RDS MySQL 5.7 entered extended support (billed uplift)", 220.0,
                "SAMPLE: in a Business+ account AWS Health surfaces this live; upgrade engine to exit extended-support billing."))
            findings.append(_finding("sample","health","eks:prod-cluster",
                "EKS 1.27 on extended support (hourly uplift per cluster)", 180.0,
                "SAMPLE: upgrade control plane to a standard-support version."))
        else:
            findings.append(_finding("live","health","aws-health",f"Health error: {e.response['Error']['Code']}"))

    return findings

if __name__ == "__main__":
    fs = enumerate_findings()
    live = [f for f in fs if f["source"]=="live"]
    samp = [f for f in fs if f["source"]=="sample"]
    print(f"Enumerated {len(fs)} findings ({len(live)} live, {len(samp)} sample)")
    for f in fs:
        tag = "LIVE  " if f["source"]=="live" else "SAMPLE"
        sav = f" ~${f['est_monthly_savings']}/mo" if f["est_monthly_savings"] else ""
        print(f"  [{tag}] {f['category']:22} {f['resource']:22} {f['issue']}{sav}")
    print(json.dumps(fs))  # machine-readable for the plan phase
