from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, List, TypeVar, Type, cast, Callable
from utils import from_none, from_str, from_float, from_datetime, from_union, relative_time, to_class, from_int, from_list, to_float, from_bool

@dataclass
class Todo:
    id: int
    text: str
    completed: bool
    created_at: datetime
    alarm_at: Optional[datetime]

    @staticmethod
    def from_dict(obj: Any) -> 'Todo':
        assert isinstance(obj, dict)
        id = from_int(obj.get("id"))
        text = from_str(obj.get("text"))
        completed = from_bool(obj.get("completed"))
        created_at = from_datetime(obj.get("created_at"))
        alarm_at = from_datetime(obj.get("alarm_at")) if "alarm_at" in obj else None
        return Todo(id, text, completed, created_at, alarm_at)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["text"] = from_str(self.text)
        result["completed"] = from_bool(self.completed)
        result["created_at"] = self.created_at.isoformat()
        if self.alarm_at:
            result["alarm_at"] = self.alarm_at.isoformat()
        return result
    
    def get_llm_text(self) -> str:
        text = f"""<todo id="{self.id}">
Created At (UTC): {self.created_at}"""
        if self.alarm_at:
            text += f"\nAlarm At (UTC): {self.alarm_at}"
        text += f"\nStatus: {'Completed' if self.completed else 'Incomplete'}"
        if self.text:
            text += f"\nText: {self.text.strip()}"
        text += "</todo>"
        return text
    
    def get_llm_summary(self) -> str:
        summary =  f"<todo id=\"{self.id}\" created=\"{relative_time(self.created_at)}\" complete=\"{self.completed}\">"
        if len(self.text) > 150:
            summary += f"{self.text[:150].strip()}..."
        else:
            summary += f"{self.text.strip()}"
        summary += "</todo>"
        return summary

def todo_from_dict(s: Any) -> List[Todo]:
    return from_list(Todo.from_dict, s)

