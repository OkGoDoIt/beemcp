from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, List, TypeVar, Type, cast, Callable
from utils import from_none, from_str, from_float, from_datetime, from_union, relative_time, relative_time_range, simple_time, simple_time_range, to_class, from_int, from_list, to_float

@dataclass
class Location:
    address: str
    latitude: float
    longitude: float
    created_at: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    id: int = None

    @staticmethod
    def from_dict(obj: Any) -> 'Location':
        assert isinstance(obj, dict)
        address = from_str(obj.get("address")).strip(", ")
        latitude = from_float(obj.get("latitude"))
        longitude = from_float(obj.get("longitude"))
        created_at = from_datetime(obj.get("created_at"))
        start_time = None
        end_time = None
        id = from_int(obj.get("id")) if "id" in obj else None
        return Location(address, latitude, longitude, created_at, start_time, end_time, id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["address"] = from_str(self.address)
        result["latitude"] = to_float(self.latitude)
        result["longitude"] = to_float(self.longitude)
        result["created_at"] = self.created_at.isoformat()
        if self.start_time is not None:
            result["start_time"] = self.start_time.isoformat()
        if self.end_time is not None:
            result["end_time"] = self.end_time.isoformat()
        if self.id is not None:
            result["id"] = from_int(self.id)
        return result
    
    def get_llm_text(self) -> str:
        id_attr = f" id=\"{self.id}\"" if self.id is not None else ""
        text = f"<location{id_attr} timestamp=\"{simple_time(self.created_at)} ({relative_time(self.created_at)})\">"
        if self.address:
            text += f"\nAddress: {self.address}"
        if self.latitude:
            text += f"\nLatitude: {self.latitude}"
        if self.longitude:
            text += f"\nLongitude: {self.longitude}"
        if self.start_time or self.end_time:
            text += f"\nTime: {simple_time_range(self.start_time, self.end_time)}"
        text += "</location>"
        return text
    
    def get_llm_summary(self) -> str:
        id_attr = f" id=\"{self.id}\"" if self.id is not None else ""
        if self.start_time or self.end_time:
            text = f"<location{id_attr} timestamp=\"{simple_time_range(self.start_time, self.end_time)})\">"
        else:
            text = f"<location{id_attr} timestamp=\"{simple_time(self.created_at)} ({relative_time(self.created_at)})\">"
        if self.address:
            text += f"{self.address}"
        elif self.latitude and self.longitude:
            text += f"lat: {self.latitude}, long: {self.longitude}"
        text += "</location>"
        return text

def location_from_dict(s: Any) -> List[Location]:
    """
    Convert a JSON dictionary to a list of Location objects.
    
    Args:
        s: JSON dictionary to convert
        
    Returns:
        List of Location objects
    """
    return from_list(Location.from_dict, s)

def combine_locations(locations: List[Location]) -> List[Location]:
    """
    Combine matching sequential locations into a single location.
    
    Args:
        locations: List of Location objects
        
    Returns:
        List of combined Location objects
    """
    combined_locations = []
    # Return empty list if no locations provided
    if not locations:
        return []
    
    # Sort locations by created_at timestamp
    sorted_locations = sorted(locations, key=lambda loc: loc.created_at)
    
    current_location = sorted_locations[0]
    for location in sorted_locations[1:]:
        if location.address == current_location.address or (location.latitude == current_location.latitude and location.longitude == current_location.longitude):
            if not current_location.start_time:
                current_location.start_time = current_location.created_at
            current_location.end_time = location.end_time or location.created_at
        else:
            combined_locations.append(current_location)
            current_location = location
    
    return combined_locations
