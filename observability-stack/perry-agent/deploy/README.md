# OIAB demo deploy artifacts (hardened, tag-based)

Source-of-truth for the live demo's infrastructure. All instance discovery is
tag-based; no ephemeral instance IDs or private IPs are hardcoded.

- `fleet-userdata.sh`        : fleet node launch-template user-data (node_exporter,
                               :05 baseline bulk-load, Phase-B pain timer, continuous
                               util churn). node_exporter scraped via Prometheus ec2_sd.
- `dvinyl-app-userdata.sh`   : dvinyl app launch-template user-data. Resolves the
                               MongoDB (dvinyl-db) private IP BY TAG at boot
                               (Role=dvinyl-db) - no hardcoded DB IP.
- `oiab-perry-web.service`   : durable systemd unit for the Perry web view (survives reboot).
- `oiab-churn.service`       : continuous low-level utilization churn (fleet).
- `oiab-fis-scheduler.service` + `fis-scheduler.sh` : random Tier-1 FIS auto-scheduler
                               (30-90 min, kill-switch aware, no-overlap guard).
- `fis-tier1-template.json`  : FIS Tier-1 experiment template. reboot/terminate are
                               scoped to Role=fleet-node ONLY; the demo-host observation
                               deck (Grafana/Prometheus/Perry) is never in the blast radius.

Stable infra IDs (VPC, SGs, launch templates, FIS templates) are referenced directly;
only ephemeral instance state is tag-resolved at runtime.
