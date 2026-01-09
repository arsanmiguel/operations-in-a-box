# Secure Monitoring Stack

Enterprise-style monitoring solution with Prometheus, Grafana, and secure API.

## Quick Start

```bash
./start.sh
```

## Services

- **Grafana**: http://localhost:3000 (admin/dWOrJpkx9cX28yQeNkJNPA)
- **Prometheus**: http://localhost:9090
- **Metrics API**: http://localhost:8080

## Security Features

✅ API Key authentication  
✅ Non-root containers  
✅ Read-only filesystems  
✅ Security headers  
✅ Input validation  
✅ Rate limiting  

## Management

```bash
docker compose up -d      # Start
docker compose down       # Stop
docker compose logs -f    # View logs
```

Generated on 2026-01-09 15:48:55
