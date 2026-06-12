# sysmon-api

A lightweight Flask REST API that exposes real-time system health metrics as JSON endpoints. Designed for DevOps monitoring, uptime checks, and system dashboards — deploy it on any Linux server and start querying CPU, memory, disk, and process data instantly.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![License](https://img.shields.io/badge/license-MIT-green)

## Endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | /health | No | Overall status: `healthy` or `degraded` |
| GET | /cpu | Yes | CPU usage %, core count, and frequency |
| GET | /memory | Yes | RAM total, available, used, and percent |
| GET | /disk | Yes | Disk total, used, free, and percent |
| GET | /processes | Yes | Top 10 processes by CPU usage |
| GET | /uptime | Yes | System uptime in human-readable format |

Auth requires an `X-API-Key` header. Set the `API_KEY` environment variable before running.

## Stack

- Python 3.10+
- Flask 3.x
- psutil 5.x

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the server:
```bash
API_KEY=your-secret-key python app.py
```

Server starts on `http://localhost:5000`.

## Example Usage

Check overall health (no auth required):
```bash
curl http://localhost:5000/health
```
```json
{"status": "healthy", "timestamp": "2024-11-15T14:32:01"}
```

Query CPU metrics:
```bash
curl -H "X-API-Key: your-secret-key" http://localhost:5000/cpu
```
```json
{"cpu_percent": 12.4, "cpu_count": 8, "cpu_freq_mhz": 2400.0}
```

Query memory usage:
```bash
curl -H "X-API-Key: your-secret-key" http://localhost:5000/memory
```
```json
{"total_gb": 16.0, "available_gb": 9.3, "used_gb": 6.7, "percent": 41.9}
```

Top processes by CPU:
```bash
curl -H "X-API-Key: your-secret-key" http://localhost:5000/processes
```

## Security

- The `/health` endpoint is intentionally unauthenticated for uptime monitor compatibility
- All other endpoints require the `X-API-Key` header
- Never hardcode the API key — load it via environment variable in production
