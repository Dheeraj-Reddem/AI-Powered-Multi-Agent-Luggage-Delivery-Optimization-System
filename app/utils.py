from datetime import datetime, timedelta
from dateutil import parser  # optional; if you don't want this, keep it simple

def parse_iso(dt_iso: str) -> datetime:
    # Using python-dateutil if available; otherwise you can use datetime.fromisoformat for simple cases.
    return parser.isoparse(dt_iso)

def to_iso(dt: datetime) -> str:
    return dt.isoformat()

def compute_pickup_time(departure_time: datetime, airport_buffer_minutes: int) -> datetime:
    return departure_time - timedelta(minutes=airport_buffer_minutes)

def rough_distance_km_from_addresses(pickup_address: str, delivery_address: str) -> float:
    # MVP placeholder: replace with Google Maps Distance Matrix later
    # Simple heuristic based on string length differences (just to keep pipeline functional)
    base = 12.0
    bump = min(25.0, (len(pickup_address) + len(delivery_address)) / 20.0)
    return base + bump

def rough_eta_minutes(distance_km: float) -> int:
    # assume ~35 km/h average => minutes = km / 35 * 60
    return max(10, int((distance_km / 35.0) * 60))
