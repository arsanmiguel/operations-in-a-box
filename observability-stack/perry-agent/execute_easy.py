#!/usr/bin/env python3
"""
OIAB Remediation Executor - the scoped-autonomy gate.

Executes ONLY the easy tier, ONLY after explicit approval, ONLY against
resources tagged Project=oiab-demo, and reversibly (snapshot before delete).

Safety rails (non-negotiable):
  - HARD SCOPE: every target is re-verified to carry tag Project=oiab-demo at
    execution time. Anything else is refused, even if the plan named it. This
    is what stops the agent from touching resources it merely *found* but does
    not own (e.g. a pre-existing stopped instance that is not ours).
  - APPROVAL GATE: requires APPROVE=yes in the environment (the "I grant you
    scoped permission" step the director described).
  - REVERSIBLE: unattached volumes are snapshotted before deletion.
  - DRY-RUN by default: set EXECUTE=yes to actually act.
"""
import os, json, sys, datetime
import boto3

REGION = os.environ.get("AWS_REGION","us-east-1")
PROJECT_TAG = ("Project","oiab-demo")

def _tagged_ok(tags):
    d = {t["Key"]:t["Value"] for t in (tags or [])}
    return d.get(PROJECT_TAG[0]) == PROJECT_TAG[1]

def remediate_easy():
    ec2 = boto3.client("ec2", region_name=REGION)
    approve = os.environ.get("APPROVE","").lower()=="yes"
    execute = os.environ.get("EXECUTE","").lower()=="yes"
    actions=[]

    # Easy-tier target class we support safely: unattached (available) volumes tagged oiab-demo.
    vols = ec2.describe_volumes(Filters=[
        {"Name":"status","Values":["available"]},
        {"Name":"tag:Project","Values":["oiab-demo"]}])["Volumes"]

    if not vols:
        print("No oiab-demo unattached volumes to remediate.")
        return actions

    print(f"Easy-tier targets (scope {PROJECT_TAG[0]}={PROJECT_TAG[1]}): {len(vols)} unattached volume(s)")
    for v in vols:
        vid, gb = v["VolumeId"], v["Size"]
        # Re-verify scope at execution time (defense in depth)
        if not _tagged_ok(v.get("Tags")):
            print(f"  REFUSED {vid}: not tagged {PROJECT_TAG[0]}={PROJECT_TAG[1]}"); continue
        plan_line = f"snapshot {vid} ({gb}GB) -> delete volume"
        if not (approve and execute):
            print(f"  [DRY-RUN] would {plan_line}  (set APPROVE=yes EXECUTE=yes to act)")
            actions.append({"resource":vid,"action":plan_line,"status":"dry-run"})
            continue
        # REVERSIBLE: snapshot first
        snap = ec2.create_snapshot(VolumeId=vid,
            Description=f"pre-remediation snapshot of {vid}",
            TagSpecifications=[{"ResourceType":"snapshot","Tags":[
                {"Key":"Project","Value":"oiab-demo"},
                {"Key":"Purpose","Value":"easy-tier-remediation-audit"},
                {"Key":"source_volume","Value":vid}]}])["SnapshotId"]
        ec2.get_waiter("snapshot_completed").wait(SnapshotIds=[snap],
            WaiterConfig={"Delay":15,"MaxAttempts":40})
        ec2.delete_volume(VolumeId=vid)
        print(f"  DONE: snapshotted {vid} -> {snap}, deleted volume {vid}")
        actions.append({"resource":vid,"action":plan_line,"status":"executed",
                        "audit_snapshot":snap})
    return actions

if __name__ == "__main__":
    print("="*72)
    print("SCOPED-AUTONOMY EXECUTOR  (easy tier, Project=oiab-demo only)")
    print(f"APPROVE={os.environ.get('APPROVE','no')}  EXECUTE={os.environ.get('EXECUTE','no')}")
    print("-"*72)
    acts = remediate_easy()
    print("-"*72)
    print(json.dumps({"executed_at":datetime.datetime.utcnow().isoformat()+"Z","actions":acts}))
    print("="*72)
