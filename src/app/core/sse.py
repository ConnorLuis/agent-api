import json
from typing import Any

def sse_event(event: str, data: dict[str, Any]) -> str:
    """
    Build a Server-Sent Events message.

    Important:
    - ensure_ascii=False keeps Chinese readable in terminal output.
    - SSE format requires a blank line between events.
    """
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"