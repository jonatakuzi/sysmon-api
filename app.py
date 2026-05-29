"""
sysmon-api: Flask REST API for real-time system health monitoring.
Exposes CPU, memory, disk, and process data as JSON endpoints.
"""

from flask import Flask, jsonify, request
import psutil
import time
import os

app = Flask(__name__)

# Set API_KEY env variable in production. Falls back to dev key.
API_KEY = os.environ.get("API_KEY", "dev-key-change-me")


def authorized():
      """Check X-API-Key header against the configured API key."""
      return request.headers.get("X-API-Key", "") == API_KEY


# Public endpoint - no auth required

@app.route("/health")
def health():
      """Overall system health status. No auth required."""
      cpu  = psutil.cpu_percent(interval=0.5)
      mem  = psutil.virtual_memory().percent
      disk = psutil.disk_usage("/").percent
      alert = cpu >= 90 or mem >= 90 or disk >= 90
      return jsonify({
          "status":         "degraded" if alert else "healthy",
          "timestamp":      int(time.time()),
          "cpu_percent":    cpu,
          "memory_percent": mem,
          "disk_percent":   disk,
      })


# Authenticated endpoints - require X-API-Key header

@app.route("/cpu")
def cpu():
      """CPU usage, count, and frequency."""
      if not authorized():
                return jsonify({"error": "Unauthorized"}), 401
            freq = psutil.cpu_freq()
    return jsonify({
              "cpu_percent":  psutil.cpu_percent(interval=1),
              "cpu_count":    psutil.cpu_count(logical=True),
              "cpu_freq_mhz": round(freq.current, 2) if freq else None,
    })


@app.route("/memory")
def memory():
      """RAM stats in GB."""
    if not authorized():
              return jsonify({"error": "Unauthorized"}), 401
          mem = psutil.virtual_memory()
    return jsonify({
              "total_gb":     round(mem.total     / 1e9, 2),
              "available_gb": round(mem.available / 1e9, 2),
              "used_gb":      round(mem.used      / 1e9, 2),
              "percent":      mem.percent,
    })


@app.route("/disk")
def disk():
      """Disk usage stats for root partition."""
    if not authorized():
              return jsonify({"error": "Unauthorized"}), 401
          d = psutil.disk_usage("/")
    return jsonify({
              "total_gb": round(d.total / 1e9, 2),
              "used_gb":  round(d.used  / 1e9, 2),
              "free_gb":  round(d.free  / 1e9, 2),
              "percent":  d.percent,
    })


@app.route("/processes")
def processes():
      """Top 10 processes by CPU usage."""
    if not authorized():
              return jsonify({"error": "Unauthorized"}), 401
          fields = ["pid", "name", "cpu_percent", "memory_percent"]
    procs = sorted(
              psutil.process_iter(fields),
              key=lambda p: p.info.get("cpu_percent") or 0,
              reverse=True
    )[:10]
    return jsonify({
              "top_processes": [
                            {
                                              "pid":            p.info["pid"],
                                              "name":           p.info["name"],
                                              "cpu_percent":    round(p.info.get("cpu_percent") or 0, 2),
                                              "memory_percent": round(p.info.get("memory_percent") or 0, 2),
                            }
                            for p in procs
              ]
    })


if __name__ == "__main__":
      app.run(debug=True, host="0.0.0.0", port=5000)
