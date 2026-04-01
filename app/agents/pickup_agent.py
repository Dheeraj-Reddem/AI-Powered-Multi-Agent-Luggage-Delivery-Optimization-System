from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import Order, AgentLog


def pickup_agent(state: dict, db: Session) -> dict:
    """
    Phase-2 Pickup agent.
    Input: state = {"order": Order, "status": "..."}
    Updates: Order.status, Order.pickup_time_iso + logs
    """
    order: Order = state["order"]

    # Mock pickup time: 2 hours before departure
    # (later replace with real scheduling logic)
    try:
        # departure_time_iso stored as ISO string; keep simple MVP behavior
        # We'll just set pickup_time_iso as "now + 30 mins" for now
        pickup_time_iso = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    except Exception:
        pickup_time_iso = datetime.utcnow().isoformat()

    order.pickup_time_iso = pickup_time_iso
    order.status = "pickup_scheduled"

    db.add(AgentLog(
        order_id=order.order_id,
        agent_name="pickup_agent",
        decision="pickup_scheduled",
        reasoning=f"Pickup scheduled at {pickup_time_iso} (mock).",
        outcome="ok",
    ))

    state["status"] = order.status
    return state