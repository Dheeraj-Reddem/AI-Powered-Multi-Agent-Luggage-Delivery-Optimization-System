from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Order, AgentLog, Tracking


def destination_delivery_agent(state: dict, db: Session) -> dict:
    order: Order = state["order"]

    # If you want to force "delivered" in MVP, set this True.
    # Later you can make it conditional (e.g., after flight_monitor says landed).
    SIMULATE_DELIVERED = True

    # Avoid re-logging if already delivered
    if order.status == "delivered":
        state["status"] = order.status
        return state

    # Step 1: mark out_for_delivery first (more realistic)
    if order.status not in {"out_for_delivery", "delivered"}:
        order.status = "out_for_delivery"

        db.add(
            AgentLog(
                order_id=order.order_id,
                agent_name="destination_delivery_agent",
                decision="out_for_delivery",
                reasoning=f"Delivery started for destination: {order.destination_address}",
                outcome="ok",
            )
        )

        # Optional: create a tracking event (GPS optional, keep 0/0 for MVP)
        db.add(
            Tracking(
                order_id=order.order_id,
                latitude=0.0,
                longitude=0.0,
                status="out_for_delivery",
                updated_at=datetime.utcnow(),
            )
        )

    # Step 2: complete delivery (mock)
    if SIMULATE_DELIVERED:
        order.status = "delivered"

        db.add(
            AgentLog(
                order_id=order.order_id,
                agent_name="destination_delivery_agent",
                decision="delivered",
                reasoning=f"Delivered to destination: {order.destination_address}",
                outcome="ok",
            )
        )

        db.add(
            Tracking(
                order_id=order.order_id,
                latitude=0.0,
                longitude=0.0,
                status="delivered",
                updated_at=datetime.utcnow(),
            )
        )

    state["status"] = order.status
    return state

