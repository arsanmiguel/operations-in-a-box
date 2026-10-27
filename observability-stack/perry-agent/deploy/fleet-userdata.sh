#!/bin/bash
set -euxo pipefail
NODE_EXPORTER_VERSION="1.8.2"
cd /tmp
curl -fsSL -o node_exporter.tar.gz "https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"
tar xzf node_exporter.tar.gz
install -m 0755 "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64/node_exporter" /usr/local/bin/node_exporter
useradd -rs /bin/false node_exporter || true
cat > /etc/systemd/system/node_exporter.service <<UNIT
[Unit]
Description=Prometheus Node Exporter
After=network.target
[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter --web.listen-address=:9100
Restart=always
[Install]
WantedBy=multi-user.target
UNIT
dnf install -y stress-ng fio || yum install -y stress-ng fio
mkdir -p /opt/oiab
cat > /opt/oiab/scheduled-bulk-load.sh <<'SH'
#!/bin/bash
set -x
TAG=scheduled-bulk-load
logger -t $TAG "START scheduled-bulk-load burst on $(hostname)"
stress-ng --cpu 4 --cpu-load 70 --timeout 240s --metrics-brief 2>&1 | logger -t $TAG
WORK=/var/tmp/${TAG}.dat
for i in 1 2 3; do
  dd if=/dev/zero of=$WORK bs=1M count=400 oflag=direct 2>&1 | logger -t $TAG || dd if=/dev/zero of=$WORK bs=1M count=400 2>&1 | logger -t $TAG
  sync
  dd if=$WORK of=/dev/null bs=1M iflag=direct 2>&1 | logger -t $TAG || dd if=$WORK of=/dev/null bs=1M 2>&1 | logger -t $TAG
done
rm -f $WORK
logger -t $TAG "END scheduled-bulk-load burst on $(hostname)"
SH
chmod +x /opt/oiab/scheduled-bulk-load.sh
cat > /etc/systemd/system/oiab-bulkload.service <<UNIT
[Unit]
Description=OIAB baseline scheduled bulk load (moderate CPU+EBS)
[Service]
Type=oneshot
ExecStart=/opt/oiab/scheduled-bulk-load.sh
UNIT
cat > /etc/systemd/system/oiab-bulkload.timer <<UNIT
[Unit]
Description=Run OIAB baseline bulk load at :05 every hour
[Timer]
OnCalendar=*-*-* *:05:00
Persistent=true
AccuracySec=15s
[Install]
WantedBy=timers.target
UNIT
cat > /opt/oiab/pain-generator.sh <<'SH'
#!/bin/bash
set -x
TAG=phase-b-pain
END=$(( $(date +%s) + 3600 ))
logger -t $TAG "START phase-b pain storm on $(hostname)"
while [ $(date +%s) -lt $END ]; do
  MODE=$(( RANDOM % 3 )); DUR=$(( (RANDOM % 120) + 30 ))
  case $MODE in
    0) logger -t $TAG "CPU spike ${DUR}s"; stress-ng --cpu 2 --cpu-load $(( (RANDOM%60)+40 )) --timeout ${DUR}s 2>&1 | logger -t $TAG ;;
    1) logger -t $TAG "EBS spike ${DUR}s"; stress-ng --hdd 2 --hdd-bytes 512m --timeout ${DUR}s 2>&1 | logger -t $TAG ;;
    2) logger -t $TAG "MEM spike ${DUR}s"; stress-ng --vm 2 --vm-bytes 60% --timeout ${DUR}s 2>&1 | logger -t $TAG ;;
  esac
  sleep $(( (RANDOM % 90) + 15 ))
done
logger -t $TAG "END phase-b pain storm on $(hostname)"
SH
chmod +x /opt/oiab/pain-generator.sh
cat > /etc/systemd/system/oiab-painb.service <<UNIT
[Unit]
Description=OIAB Phase B pain storm (unpredictable CPU/EBS/MEM)
[Service]
Type=oneshot
ExecStart=/opt/oiab/pain-generator.sh
UNIT
cat > /etc/systemd/system/oiab-painb.timer <<UNIT
[Unit]
Description=Fire OIAB Phase B pain storm once at 2026-10-14 14:50 UTC
[Timer]
OnCalendar=2026-10-14 14:50:00 UTC
Persistent=false
AccuracySec=10s
[Install]
WantedBy=timers.target
UNIT
systemctl daemon-reload
systemctl enable --now node_exporter
systemctl enable --now oiab-bulkload.timer
systemctl enable --now oiab-painb.timer
# --- continuous low-level utilization churn ---
cat > /opt/oiab/churn.sh <<'CHURN'
#!/bin/bash
set +e
TAG=util-churn
while true; do
  MODE=$(( RANDOM % 4 )); DUR=$(( (RANDOM % 40) + 20 ))
  case $MODE in
    0) stress-ng --cpu 1 --cpu-load $(( (RANDOM%30)+10 )) --timeout ${DUR}s >/dev/null 2>&1 ;;
    1) stress-ng --cpu 2 --cpu-load $(( (RANDOM%25)+10 )) --timeout ${DUR}s >/dev/null 2>&1 ;;
    2) stress-ng --vm 1 --vm-bytes 20% --timeout ${DUR}s >/dev/null 2>&1 ;;
    3) stress-ng --hdd 1 --hdd-bytes 128m --timeout ${DUR}s >/dev/null 2>&1 ;;
  esac
  sleep $(( (RANDOM % 50) + 20 ))
done
CHURN
chmod +x /opt/oiab/churn.sh
cat > /etc/systemd/system/oiab-churn.service <<'UNIT'
[Unit]
Description=OIAB continuous low-level utilization churn
After=network.target
[Service]
Type=simple
ExecStart=/opt/oiab/churn.sh
Restart=always
Nice=10
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now oiab-churn.service
