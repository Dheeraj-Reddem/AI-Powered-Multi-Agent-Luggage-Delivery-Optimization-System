from pydantic import BaseModel, Field

class OrderCreate(BaseModel):
    # Customer
    user_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=7, max_length=30)


    flight_number: str
    departure_airport: str
    departure_time_iso: str  # built from UI date + time + timezone

    # Pickup
    pickup_address: str

    # Phase-2: final delivery after arrival
    destination_address: str

    # Phase-2: passenger details for airline check-in
    passenger_first_name: str = Field(min_length=1, max_length=80)
    passenger_last_name: str = Field(min_length=1, max_length=80)
    pnr: str = Field(min_length=3, max_length=20)

    # Luggage
    luggage_count: int = Field(ge=1, le=10)
    luggage_weight_kg: float = Field(ge=0.1, le=200.0)


class OrderOut(BaseModel):
    order_id: str
    status: str

    pickup_time_iso: str | None = None
    eta_to_airport_minutes: int | None = None
    distance_km: float | None = None
    total_price: float | None = None

    # Phase-2 additions
    airline_integration_status: str | None = None
    checkin_confirmation_code: str | None = None
    boarding_pass_url: str | None = None

    bagdrop_status: str | None = None
    bagdrop_appointment_time_iso: str | None = None
    bagdrop_facility: str | None = None

    destination_delivery_status: str | None = None
    destination_delivery_eta_iso: str | None = None

    phase2_error: str | None = None


class TrackingCreate(BaseModel):
    latitude: float
    longitude: float
    status: str = "in_transit"

class AgentRunOut(BaseModel):
    order_id: str
    celery_task_id: str
    status: str
