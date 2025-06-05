from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, List, TypeVar, Type, cast, Callable
from .utils import from_none, from_str, from_optional_str, from_float, from_datetime, from_union, relative_time_range, to_class, from_int, from_list, to_float
from .location import Location

@dataclass
class Conversation:
    id: int
    start_time: datetime
    end_time: datetime
    device_type: str
    summary: str
    short_summary: str
    state: str
    created_at: datetime
    updated_at: datetime
    primary_location: Optional[Location] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Conversation':
        assert isinstance(obj, dict)
        id = from_int(obj.get("id"))
        start_time = from_datetime(obj.get("start_time"))
        end_time = from_datetime(obj.get("end_time"))
        device_type = from_str(obj.get("device_type"))
        summary = from_optional_str(obj.get("summary"))
        short_summary = from_optional_str(obj.get("short_summary"))
        state = from_str(obj.get("state"))
        created_at = from_datetime(obj.get("created_at"))
        updated_at = from_datetime(obj.get("updated_at"))
        primary_location = from_union([Location.from_dict, from_none], obj.get("primary_location"))
        return Conversation(id, start_time, end_time, device_type, summary, short_summary, state, created_at, updated_at, primary_location)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["start_time"] = self.start_time.isoformat()
        result["end_time"] = self.end_time.isoformat()
        result["device_type"] = from_str(self.device_type)
        result["summary"] = from_str(self.summary)
        result["short_summary"] = from_str(self.short_summary)
        result["state"] = from_str(self.state)
        result["created_at"] = self.created_at.isoformat()
        result["updated_at"] = self.updated_at.isoformat()
        result["primary_location"] = from_union([lambda x: to_class(Location, x), from_none], self.primary_location)
        return result

    def get_llm_text(self) -> str:
        text = f"""<conversation id="{self.id}">
Conversation URI: bee://conversations/{self.id}
Time: {relative_time_range(self.start_time, self.end_time)}"""
        if self.primary_location and self.primary_location.address:
            text += f"\nPrimary Location: {self.primary_location.address or 'Unknown'}"
        if self.short_summary:
            text += f"\nShort Summary: {self.short_summary.strip()}"
        if self.summary:
            fixed_summary = self.summary
            if fixed_summary.startswith("**Summary**\n"):
                fixed_summary = fixed_summary[13:]
            fixed_summary = fixed_summary.replace("Summary: ", "").strip()
            fixed_summary = fixed_summary.replace("**Summary**", "").strip()
            fixed_summary = fixed_summary.replace("## Summary\n", "").strip()
            fixed_summary = fixed_summary.replace("\n\n## Atmosphere\n", "\nAtmosphere: ").strip()
            fixed_summary = fixed_summary.replace("\n\nAtmosphere\n", "\nAtmosphere: ").strip()
            fixed_summary = fixed_summary.replace("\n\n## Key Take Aways\n", "\nKey Take Aways: ").strip()
            fixed_summary = fixed_summary.replace("\n\nKey Take Aways\n", "\nKey Take Aways: ").strip()
            fixed_summary = fixed_summary.replace("\n\n## Key Takeaways\n", "\nKey Takeaways: ").strip()
            fixed_summary = fixed_summary.replace("\n\nKey Takeaways\n", "\nKey Takeaways: ").strip()
            text += f"\nSummary: {fixed_summary.strip()}"
        text += "</conversation>"
        return text

    def get_llm_summary(self) -> str:
        text = f"""<conversation id="{self.id}">
Time: {relative_time_range(self.start_time, self.end_time)}"""
        if self.short_summary:
            text += f"\nShort Summary: {self.short_summary.strip()}"
        text += "</conversation>"
        return text


def conversation_from_dict(s: Any) -> List[Conversation]:
    return from_list(Conversation.from_dict, s)
