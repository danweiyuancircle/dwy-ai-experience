"""Unified API response helpers."""

import time
from typing import Any


def success(data: Any = None, message: str = "success") -> dict:
    """Return a 200 OK response envelope."""
    return {"code": 200, "message": message, "data": data, "timestamp": int(time.time())}


def fail(code: int = 400, message: str = "fail") -> dict:
    """Return an error response envelope."""
    return {"code": code, "message": message, "data": None, "timestamp": int(time.time())}


def paginated(items: list, total: int, page: int, page_size: int) -> dict:
    """Return a 200 OK envelope containing paginated list metadata."""
    return success(data={"items": items, "total": total, "page": page, "page_size": page_size})
