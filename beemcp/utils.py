from datetime import datetime
from typing import Any, Optional, List, TypeVar, Type, cast, Callable


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_datetime(x: Any) -> datetime:
    # Parse datetime string in ISO format (e.g., "2025-03-18T18:32:12.178Z")
    # for standard ISO format timestamps
    if isinstance(x, str):
        if x.endswith('Z'):
            # Convert UTC 'Z' timezone marker to +00:00 format that fromisoformat understands
            x = x[:-1] + '+00:00'
        return datetime.fromisoformat(x)
    return x


def to_float(x: Any) -> float:
    assert isinstance(x, (int, float))
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x

def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x

def to_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    if isinstance(x, list):
        return [f(y) for y in x]
    else:
        return [f(x)]

def simple_time_range(start: datetime, end: datetime) -> str:
    if start and end:
        if relative_time(start) == relative_time(end):
            return f"{simple_time(start)} - {simple_time(end)} ({relative_time_range(start, end, delta_only=True)} long, {relative_time(start)})"
        else:
            return f"{simple_time(start)} ({relative_time(start)}) - {simple_time(end)} ({relative_time(end)}) ({relative_time_range(start, end, delta_only=True)} long)"
    elif start:
        return f"{simple_time(start)} ({relative_time(start)})"
    elif end:
        return f"{simple_time(end)} ({relative_time(end)})"
    else:
        return ""

def relative_time_range(start: datetime, end: datetime, delta_only=False) -> str:
    delta = end - start
    start_text = relative_time(start)
    if delta.seconds > 60 * 60:
        delta_text = f"{delta.seconds // (60 * 60)} hours"
    elif delta.seconds > 60:
        delta_text = f"{delta.seconds // 60} minutes"
    else:
        delta_text = f"{delta.seconds} seconds"
    if delta_only:
        return delta_text
    return f"{start_text} ({delta_text} long)"

def relative_time(x: datetime) -> str:
    """
    Returns a human-readable relative time string (e.g., "2 days ago").
    Handles both timezone-aware and timezone-naive datetime objects.
    
    Args:
        x: The datetime to compare against current time
        
    Returns:
        A string representing the relative time
    """
    # Ensure both datetimes have the same timezone awareness
    now = datetime.now(x.tzinfo) if x.tzinfo else datetime.now()
    
    delta = now - x
    if delta.days > 365:
        return f"{delta.days // 365} years ago"
    elif delta.days > 30:
        return f"{delta.days // 30} months ago"
    elif delta.days > 7:
        return f"{delta.days // 7} weeks ago"
    elif delta.days > 1:
        return f"{delta.days} days ago"
    elif delta.days == 1:
        return "yesterday"
    elif delta.seconds >= 3600:  # Use seconds instead of hours attribute
        return "today"
    else:
        return "recently"

def simple_time(x: datetime) -> str:
    return x.strftime("%Y-%m-%d %H:%M (UTC)")
