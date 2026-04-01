import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

def _uuid() -> str:
    return str(uuid.uuid4())

class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(30))

    flight_number: Mapped[str] = mapped_column(String(30))
    departure_airport: Mapped[str] = mapped_column(String(10))
    departure_time_iso: Mapped[str] = mapped_column(String(40))  # ISO string for MVP

    pickup_address: Mapped[str] = mapped_column(Text)
    delivery_address: Mapped[str] = mapped_column(Text)  # airport terminal etc.
    
    destination_address: Mapped[str] = mapped_column(Text, default="")
    airline_integration_status: Mapped[str] = mapped_column(String(30), default="unknown")

    luggage_count: Mapped[int] = mapped_column()
    luggage_weight_kg: Mapped[float] = mapped_column(Float)

    pickup_time_iso: Mapped[str | None] = mapped_column(String(40), nullable=True)
    eta_to_airport_minutes: Mapped[int | None] = mapped_column(nullable=True)

    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_price: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(30), default="initiated")
    agent_result_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    logs: Mapped[list["AgentLog"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    trackings: Mapped[list["Tracking"]] = relationship(back_populates="order", cascade="all, delete-orphan")

    destination_delivery_status: Mapped[str] = mapped_column(String(30), default="pending")
    destination_delivery_eta_iso: Mapped[str | None] = mapped_column(String(40), nullable=True)

    phase2_error: Mapped[str | None] = mapped_column(Text, nullable=True)


class AgentLog(Base):
    __tablename__ = "agent_logs"

    log_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(String, ForeignKey("orders.order_id"), index=True)

    agent_name: Mapped[str] = mapped_column(String(60))
    decision: Mapped[str] = mapped_column(Text)
    reasoning: Mapped[str] = mapped_column(Text)
    outcome: Mapped[str] = mapped_column(String(40), default="ok")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order: Mapped["Order"] = relationship(back_populates="logs")


class Tracking(Base):
    __tablename__ = "tracking"

    tracking_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(String, ForeignKey("orders.order_id"), index=True)

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="in_transit")

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order: Mapped["Order"] = relationship(back_populates="trackings")
from sqlalchemy import Boolean, Integer

class Passenger(Base):
    __tablename__ = "passengers"
    passenger_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)

    order_id: Mapped[str] = mapped_column(String, ForeignKey("orders.order_id"), index=True)

    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))

    # airline booking reference (PNR)
    pnr: Mapped[str] = mapped_column(String(20), index=True)

    # optional (international/extra verification later)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Bag(Base):
    __tablename__ = "bags"
    bag_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(String, ForeignKey("orders.order_id"), index=True)

    weight_kg: Mapped[float] = mapped_column(Float)
    seal_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # bag tag barcode returned by airline/partner system (or generated)
    tag_barcode: Mapped[str | None] = mapped_column(String(64), nullable=True)

    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)  # later store in S3
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AirlineCheckin(Base):
    __tablename__ = "airline_checkins"
    checkin_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(String, ForeignKey("orders.order_id"), index=True)

    airline_code: Mapped[str] = mapped_column(String(10))  # e.g. "UA"
    flight_number: Mapped[str] = mapped_column(String(30))

    status: Mapped[str] = mapped_column(String(30), default="not_started")
    confirmation_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    boarding_pass_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # if integration failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class BagDrop(Base):
    __tablename__ = "bag_drops"
    bagdrop_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(String, ForeignKey("orders.order_id"), index=True)

    status: Mapped[str] = mapped_column(String(30), default="not_scheduled")
    facility: Mapped[str | None] = mapped_column(String(120), nullable=True)  # counter/facility name
    appointment_time_iso: Mapped[str | None] = mapped_column(String(40), nullable=True)

    accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    accepted_time_iso: Mapped[str | None] = mapped_column(String(40), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

