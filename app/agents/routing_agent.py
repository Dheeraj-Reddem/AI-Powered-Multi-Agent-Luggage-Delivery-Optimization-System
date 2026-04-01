from app.models import AgentLog
from app.utils import rough_distance_km_from_addresses, rough_eta_minutes

def routing_agent(state, db):
    order = state["order"]

    distance_km = rough_distance_km_from_addresses(order.pickup_address, order.delivery_address)
    eta = rough_eta_minutes(distance_km)

    order.distance_km = float(distance_km)
    order.eta_to_airport_minutes = int(eta)
    order.status = "route_planned"

    db.add(AgentLog(
        order_id=order.order_id,
        agent_name="routing_agent",
        decision=f"distance_km={order.distance_km}, eta_minutes={order.eta_to_airport_minutes}",
        reasoning="MVP heuristic routing; replace with Maps API later.",
        outcome="ok",
    ))

    state["status"] = "route_planned"
    return state
