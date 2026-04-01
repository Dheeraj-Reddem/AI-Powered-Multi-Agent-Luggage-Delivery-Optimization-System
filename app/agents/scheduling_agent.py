from app.models import AgentLog
from app.settings import settings
from app.utils import parse_iso, compute_pickup_time, to_iso

def scheduling_agent(state, db):
    order = state["order"]
    departure = parse_iso(order.departure_time_iso)
    pickup_dt = compute_pickup_time(departure, settings.AIRPORT_BUFFER_MINUTES)

    order.pickup_time_iso = to_iso(pickup_dt)
    order.status = "scheduled"

    db.add(AgentLog(
        order_id=order.order_id,
        agent_name="scheduling_agent",
        decision=f"Set pickup_time_iso={order.pickup_time_iso}",
        reasoning=f"Applied airport buffer of {settings.AIRPORT_BUFFER_MINUTES} minutes before departure.",
        outcome="ok"
    ))

    state["status"] = "scheduled"
    return state
