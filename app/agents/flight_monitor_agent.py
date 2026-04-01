from sqlalchemy.orm import Session
from app.models import Order, AgentLog


def flight_monitor_agent(state: dict, db: Session) -> dict:
    order: Order = state["order"]

    # MVP: instantly mark arrived (later poll real flight API)
    order.status = "arrived"

    db.add(AgentLog(
        order_id=order.order_id,
        agent_name="flight_monitor_agent",
        decision="flight_arrived",
        reasoning="Mock flight status: arrived.",
        outcome="ok",
    ))

    state["status"] = order.status
    return state
