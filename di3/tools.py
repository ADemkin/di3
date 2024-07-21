from typing import Any


def name(obj: Any) -> str:
    if not hasattr(obj, "__name__"):
        obj = obj.__class__
    return str(obj.__name__)
