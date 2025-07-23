# runtime_tracer.py — Capture real-time trace context (placeholder logic)

import json

def get_runtime_trace(log_path: str = "runtime_logs/trace.json") -> str:
    try:
        with open(log_path, "r") as f:
            logs = json.load(f)
        recent_logs = logs[-5:] if isinstance(logs, list) else [logs]
        return "\n\n".join(json.dumps(entry, indent=2)[:1000] for entry in recent_logs)
    except Exception as e:
        return f"[Error fetching trace: {e}]"
