# ✅ runtime_tracer.py — Trace Log Extractor

import json
import os

def get_runtime_trace_log(trace_path: str) -> str:
    try:
        if not os.path.exists(trace_path):
            return f"Trace file not found at {trace_path}"

        with open(trace_path, "r") as f:
            trace_data = json.load(f)

        if isinstance(trace_data, list):
            entries = trace_data[-3:]
        elif isinstance(trace_data, dict):
            entries = [trace_data]
        else:
            return "Trace file format is not supported."

        formatted = "\n\n".join(json.dumps(entry, indent=2) for entry in entries)
        return formatted

    except Exception as e:
        return f"Error reading trace log: {str(e)}"
