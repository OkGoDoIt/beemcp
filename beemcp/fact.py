from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, List, TypeVar, Type, cast, Callable
from .utils import from_none, from_str, from_float, from_datetime, from_union, relative_time, to_class, from_int, from_list, to_float, from_bool

@dataclass
class Fact:
    id: int
    text: str
    tags: List[str]
    created_at: datetime
    visibility: str
    confirmed: Optional[bool] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Fact':
        assert isinstance(obj, dict)
        id = from_int(obj.get("id"))
        text = from_str(obj.get("text"))
        tags = from_list(from_str, obj.get("tags"))
        created_at = from_datetime(obj.get("created_at"))
        visibility = from_str(obj.get("visibility"))
        confirmed = from_bool(obj.get("confirmed")) if "confirmed" in obj else None
        return Fact(id, text, tags, created_at, visibility, confirmed)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["text"] = from_str(self.text)
        result["tags"] = from_list(from_str, self.tags)
        result["created_at"] = self.created_at.isoformat()
        result["visibility"] = from_str(self.visibility)
        result["confirmed"] = from_bool(self.confirmed) if self.confirmed is not None else None
        return result
    
    def get_llm_text(self) -> str:
        text = f"""<fact id="{self.id}">
Recorded at (UTC): {self.created_at}
Tags: {', '.join(self.tags)}"""
        if self.confirmed is False:
            text += f"\nTHIS IS UNCONFIRMED (it may be implied, but take it with a grain of salt)"
        elif self.confirmed is True:
            text += f"\n(This fact has been confirmed by the user)"
        if self.text:
            text += f"\nContent: {self.text.strip()}"
        text += "</fact>"
        return text
    
    def get_llm_summary(self) -> str:
        confirmed_text = " confirmed=\"true\"" if self.confirmed else ""
        return f"<fact id=\"{self.id}\" recorded=\"{relative_time(self.created_at)}\"{confirmed_text}>{self.text.strip()}</fact>"


def fact_from_dict(s: Any) -> List[Fact]:
    return from_list(Fact.from_dict, s)

