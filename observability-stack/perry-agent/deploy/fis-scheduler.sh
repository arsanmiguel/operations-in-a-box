#!/bin/bash
# Fire a random Tier-1 (recoverable) FIS experiment, guarded:
#  - skip if kill-switch alarm is in ALARM
#  - skip if a Tier-1 experiment is already running (no overlap)
# Then reschedule self for a random 30-90 min from now.
set +e
REGION=us-east-1
TMPL=EXTCAfmXAxCPNHX9i   # Tier 1 recoverable storm (ONLY this auto-fires)
TAG=fis-scheduler
log(){ logger -t $TAG "$1"; echo "$(date -u +%FT%TZ) $1" >> /var/log/oiab-fis-scheduler.log; }

# kill-switch check
STATE=$(aws cloudwatch describe-alarms --region $REGION --alarm-names oiab-chaos-killswitch --query 'MetricAlarms[0].StateValue' --output text 2>/dev/null)
if [ "$STATE" = "ALARM" ]; then log "kill-switch ALARM; skipping"; else
  # no-overlap check
  RUNNING=$(aws fis list-experiments --region $REGION --query "length(experiments[?experimentTemplateId=='$TMPL' && (state.status=='running' || state.status=='initiating' || state.status=='pending')])" --output text 2>/dev/null)
  if [ "${RUNNING:-0}" != "0" ]; then log "Tier-1 already running ($RUNNING); skipping"; else
    EID=$(aws fis start-experiment --region $REGION --experiment-template-id $TMPL --tags Project=oiab-demo,Tier=1,Trigger=auto-scheduler --query 'experiment.id' --output text 2>/dev/null)
    log "started Tier-1 experiment $EID"
  fi
fi

# self-reschedule: random 30-90 min
MINS=$(( (RANDOM % 61) + 30 ))
NEXT=$(date -u -d "+${MINS} min" +%Y-%m-%d\ %H:%M:%S 2>/dev/null || date -u -v+${MINS}M +%Y-%m-%d\ %H:%M:%S)
systemctl stop oiab-fis-scheduler.timer 2>/dev/null
cat > /etc/systemd/system/oiab-fis-scheduler.timer <<UNIT
[Unit]
Description=Random Tier-1 FIS scheduler (self-reschedules)
[Timer]
OnCalendar=${NEXT} UTC
Persistent=false
AccuracySec=30s
[Install]
WantedBy=timers.target
UNIT
systemctl daemon-reload
systemctl start oiab-fis-scheduler.timer
log "next Tier-1 scheduled in ${MINS} min (${NEXT} UTC)"

