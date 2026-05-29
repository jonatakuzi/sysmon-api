"""
sysmon-api - Flask REST API for real-time system health monitoring.
Exposes CPU, memory, disk, process, and uptime data as JSON endpoints.

Public endpoint:    /health   (no auth needed - safe for uptime monitors)
Protected endpoints: /cpu, /memory, /disk, /processes, /uptime
  - All require an X-API-Key header to prevent unauthorized access
"""

from flask import Flask, jsonify, request
import psutil
import time
import os
import datetime

app = Flask(__name__)

# API key is loaded from an environment variable so it is never hardcoded.
# Set it in production with: export API_KEY=your-secret-key
API_KEY = os.environ.get("API_KEY", "dev-key-change-me")


def authorized():
    """Return True if the request includes the correct API key in the header."""
    return request.headers.get("X-API-Key", "") == API_KEY


@app.route("/health")
def health():
    """
    Public - no auth needed.
    Returns overall system status: 'healthy' or 'degraded'.
    Meant for uptime monitors or load balancers that need a quick pulse check.
    Flags 'degraded' if any resource hits 90% or above.
    """
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    alert = cpu >= 90 or mem >= 90 or disk >= 90
    return jsonify({
        "status": "degraded" if alert else "healthy",
        "timestamp": int(time.time()),
        "cpu_percent": cpu,
        "memory_percent": mem,
        "disk_percent": disk
    })


@app.route("/cpu")
def cpu():
    """
    Protected - requires X-API-Key header.
    Returns CPU usage percent, logical and physical core counts, and clock speed.
    Physical vs logical counts differ when hyper-threading is enabled.
    """
    if not authorized():
        return jsonify({"error": "Unauthorized"}), 401
    freq = psutil.cpu_freq()
    return jsonify({
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "cpu_freq_mhz": round(freq.current, 2) if freq else None
    })


@app.route("/memory")
def memory():
    """
    Protected - requires X-API-Key header.
    Returns RAM stats converted to MB for readability.
    Tracking available vs used helps spot memory leaks in long-running services.
    """
    if not authorized():
        return jsonify({"error": "Unauthorized"}), 401
    mem = psutil.virtual_memory()
    return jsonify({
        "total_mb": round(mem.total / 1024 / 1024, 2),
        "available_mb": round(mem.available / 1024 / 1024, 2),
        "used_mb": round(mem.used / 1024 / 1024, 2),
        "percent": mem.percent
    })


@app.route("/disk")
def disk():
    """
    Protected - requires X-API-Key header.
    Returns disk usage for the root filesystem converted to GB.
    """
    if not authorized():
        return jsonify({"error": "Unauthorized"}), 401
    d = psutil.disk_usage("/")
    return jsonify({
        "total_gb": round(d.total / 1024 / 1024 / 1024, 2),
        "used_gb": round(d.used / 1024 / 1024 / 1024, 2),
        "free_gb": round(d.free / 1024 / 1024 / 1024, 2),
        "percent": d.percent
    })


@app.route("/processes")
def processes():
    """
    Protected - requires X-API-Key header.
    Returns the top 10 running processes sorted by CPU usage.
    AccessDenied is caught for system processes the user cannot inspect.
    """
    if not authorized():
        return jsonify({"error": "Unauthorized"}), 401
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    top = sorted(procs, key=lambda x: x["cpu_percent"] or 0, reverse=True)[:10]
    return jsonify({"processes": top})


@app.route("/uptime")
def uptime():
    """
    Protected - requires X-API-Key header.
    Returns how long the system has been running since last boot.
    Useful for monitoring server restarts or unexpected reboots.
    """
    if not authorized():
        return jsonify({"error": "Unauthorized"}), 401
    boot_ts = psutil.boot_time()
    uptime_secs = int(time.time() - boot_ts)
    boot_str = datetime.datetime.fromtimestamp(boot_ts).strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({
        "boot_time": boot_str,
        "uptime_seconds": uptime_secs,
        "uptime_human": str(datetime.timedelta(seconds=uptime_secs))
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
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
