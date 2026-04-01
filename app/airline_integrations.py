from dataclasses import dataclass
from typing import Protocol
import httpx

@dataclass
class CheckinResult:
    status: str              # "success" | "failed"
    confirmation_code: str | None = None
    boarding_pass_url: str | None = None
    error_message: str | None = None

@dataclass
class BagDropResult:
    status: str              # "scheduled" | "failed"
    facility: str | None = None
    appointment_time_iso: str | None = None
    error_message: str | None = None

class AirlineAdapter(Protocol):
    async def check_in(self, *, airline_code: str, flight_number: str, pnr: str, last_name: str) -> CheckinResult: ...
    async def schedule_bag_drop(self, *, airline_code: str, flight_number: str, pnr: str) -> BagDropResult: ...

class MockPartnerAdapter:
    """
    Phase-2 scaffold: behaves like an airline partner API.
    Replace methods with real partner endpoints when you have them.
    """
    async def check_in(self, *, airline_code: str, flight_number: str, pnr: str, last_name: str) -> CheckinResult:
        # simulate success for now
        return CheckinResult(
            status="success",
            confirmation_code=f"{pnr}-{airline_code}",
            boarding_pass_url=f"https://example.com/boardingpass/{pnr}"
        )

    async def schedule_bag_drop(self, *, airline_code: str, flight_number: str, pnr: str) -> BagDropResult:
        # simulate scheduling
        return BagDropResult(
            status="scheduled",
            facility=f"{airline_code} BagDrop Counter",
            appointment_time_iso=None,
        )

def get_adapter_for_airline(airline_code: str) -> AirlineAdapter:
    # later: return real adapter by airline
    return MockPartnerAdapter()