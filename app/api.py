from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import OrderCreate, OrderOut, TrackingCreate, AgentRunOut
from app.worker import process_order
from app.models import (
    Order, Tracking, Passenger, Bag,
    AgentLog, BagDrop
)

router = APIRouter()
@router.post("/orders", response_model=AgentRunOut)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    order = Order(
        user_name=payload.user_name,
        phone=payload.phone,
        flight_number=payload.flight_number,
        departure_airport=payload.departure_airport,
        departure_time_iso=payload.departure_time_iso,
        pickup_address=payload.pickup_address,

        # make safe for Phase-2 (optional field)
        delivery_address=getattr(payload, "delivery_address", "") or "",

        destination_address=payload.destination_address,
        luggage_count=payload.luggage_count,
        luggage_weight_kg=float(payload.luggage_weight_kg),
        status="initiated",
        airline_integration_status="unknown",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # passenger info
    p = Passenger(
        order_id=order.order_id,
        first_name=payload.passenger_first_name,
        last_name=payload.passenger_last_name,
        pnr=payload.pnr,
    )
    db.add(p)

    # create bag rows (split weight evenly for MVP)
    per_bag = float(payload.luggage_weight_kg) / max(1, payload.luggage_count)
    for _ in range(payload.luggage_count):
        db.add(Bag(order_id=order.order_id, weight_kg=per_bag))

    db.commit()

    # trigger workflow
    task = process_order.delay(order.order_id)

    # return actual order status (not a made-up string)
    return {"order_id": order.order_id, "celery_task_id": task.id, "status": order.status}

@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Latest bagdrop row (real bagdrop status + appointment time)
    latest_bagdrop = (
        db.query(BagDrop)
        .filter(BagDrop.order_id == order_id)
        .order_by(BagDrop.created_at.desc())
        .first()
    )

    bagdrop_status = latest_bagdrop.status if latest_bagdrop else None
    bagdrop_time = latest_bagdrop.appointment_time_iso if latest_bagdrop else None

    # Destination delivery status derived from overall order.status
    if order.status == "delivered":
        destination_delivery_status = "delivered"
    elif order.status == "failed":
        destination_delivery_status = "failed"
    else:
        destination_delivery_status = "pending"

    # Pull last error message from agent logs (if any)
    last_error_log = (
        db.query(AgentLog)
        .filter(AgentLog.order_id == order_id)
        .filter(AgentLog.outcome.in_(["error", "failed"]))
        .order_by(AgentLog.created_at.desc())
        .first()
    )

    phase2_error = None
    if last_error_log:
        phase2_error = last_error_log.reasoning or last_error_log.decision
    elif order.status == "failed":
        phase2_error = "Order failed (check logs)"

    return OrderOut(
        order_id=order.order_id,
        status=order.status,

        pickup_time_iso=order.pickup_time_iso,
        eta_to_airport_minutes=order.eta_to_airport_minutes,
        distance_km=order.distance_km,
        total_price=order.total_price,

        airline_integration_status=order.airline_integration_status,

        bagdrop_status=bagdrop_status,
        bagdrop_appointment_time_iso=bagdrop_time,

        destination_delivery_status=destination_delivery_status,
        phase2_error=phase2_error,
    )



@router.post("/orders/{order_id}/tracking")
def add_tracking(order_id: str, payload: TrackingCreate, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    t = Tracking(
        order_id=order_id,
        latitude=float(payload.latitude),
        longitude=float(payload.longitude),
        status=payload.status
    )
    db.add(t)
    # optionally also update order status from tracking
    if payload.status in {"picked_up", "in_transit", "delivered"}:
        order.status = payload.status

    db.commit()
    return {"ok": True}

@router.get("/orders/{order_id}/logs")
def get_logs(order_id: str, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return [
        {
            "agent_name": log.agent_name,
            "decision": log.decision,
            "reasoning": log.reasoning,
            "outcome": log.outcome,
            "created_at": log.created_at.isoformat(),
        }
        for log in order.logs
    ]
