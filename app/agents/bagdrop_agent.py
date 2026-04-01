from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import Order, AgentLog, BagDrop


def bagdrop_agent(state: dict, db: Session) -> dict:
    order: Order = state["order"]

    # 1) Find existing BagDrop row (idempotent)
    bagdrop = (
        db.query(BagDrop)
        .filter(BagDrop.order_id == order.order_id)
        .order_by(BagDrop.created_at.desc())
        .first()
    )

    # 2) Compute a reasonable appointment time
    # If pickup_time_iso exists, reuse it; else create an appointment ~2 hours from now (MVP fallback)
    appt_iso = order.pickup_time_iso
    if not appt_iso:
        appt_iso = (datetime.utcnow() + timedelta(hours=2)).replace(microsecond=0).isoformat() + "Z"
        order.pickup_time_iso = appt_iso  # optional: keep pickup time aligned

    facility = f"{order.departure_airport} BagDrop Counter A"

    # 3) Create if missing, otherwise update
    if not bagdrop:
        bagdrop = BagDrop(order_id=order.order_id)
        db.add(bagdrop)

    bagdrop.status = "scheduled"
    bagdrop.facility = facility
    bagdrop.appointment_time_iso = appt_iso

    # For Phase-2: keep accepted False until you explicitly "accept" later
    bagdrop.accepted = False
    bagdrop.accepted_time_iso = None

    # 4) Update order status (scheduled, not dropped yet)
    order.status = "bagdrop_scheduled"

    # 5) Log it
    db.add(
        AgentLog(
            order_id=order.order_id,
            agent_name="bagdrop_agent",
            decision="bagdrop_scheduled",
            reasoning=f"Bag drop scheduled at {facility} for {appt_iso}.",
            outcome="ok",
        )
    )

    state["status"] = order.status
    return state
