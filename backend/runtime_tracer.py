def get_runtime_trace(event: str, action: str, api_call: str):
    return f"User event '{event}' triggers action '{action}' which calls API: {api_call}"
