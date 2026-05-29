# sysmon-api

A lightweight Flask REST API that exposes real-time system health metrics as JSON endpoints. Built with Python, Flask, and psutil.

## Endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| GET | /health | No | Overall status: healthy or degraded |
| GET | /cpu | Yes | CPU usage, core count, and frequency |
| GET | /memory | Yes | RAM total, available, used, and percent |
| GET | /disk | Yes | Disk total, used, free, and percent |
| GET | /processes | Yes | Top 10 processes by CPU usage |

Auth uses an X-API-Key request header. Set the API_KEY environment variable before running.

## Stack

- Python 3.10+
- - Flask 3.x
  - - psutil 5.x
   
    - ## Setup
   
    - Install dependencies:
   
    -     pip install -r requirements.txt
   
    - Run the server:
   
    -     API_KEY=your-secret-key python app.py
   
    - Server starts on http://localhost:5000
   
    - ## Example Usage
   
    - Check overall health (no auth):
   
    -     curl http://localhost:5000/health
   
    - Sample response:
   
    -     {
    -       "status": "healthy",
    -         "timestamp": 1748478000,
    -           "cpu_percent": 14.2,
    -             "memory_percent": 61.5,
    -               "disk_percent": 42.8
    -               }
   
    -           Get CPU details (auth required):
   
    -           curl -H "X-API-Key: your-secret-key" http://localhost:5000/cpu
   
    -       Get top 10 processes:
   
    -       curl -H "X-API-Key: your-secret-key" http://localhost:5000/processes
   
    -   ## Project Structure
   
    -       sysmon-api/
    -       +-- app.py            # Flask app with all route handlers
    -       +-- requirements.txt  # Flask and psutil dependencies
   
    -   ## Notes
   
    -   The /health endpoint is public so monitoring tools can poll it without credentials. All metric endpoints require the API key. Resources above 90 percent utilization trigger a "degraded" status in /health.
