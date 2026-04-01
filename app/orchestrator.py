from langgraph.graph import StateGraph

from app.agents.booking_agent import booking_agent
from app.agents.scheduling_agent import scheduling_agent
from app.agents.pickup_agent import pickup_agent
from app.agents.airline_checkin_agent import airline_checkin_agent
from app.agents.bagdrop_agent import bagdrop_agent
from app.agents.flight_monitor_agent import flight_monitor_agent
from app.agents.destination_delivery_agent import destination_delivery_agent
from app.agents.routing_agent import routing_agent
from app.agents.pricing_agent import pricing_agent
from app.agents.exception_agent import exception_agent


def build_graph():
    """
    Graph is optional right now because the worker runs node_sequence manually.
    But we keep it accurate for documentation + future LangGraph execution.
    State is dict: {"order": Order, "status": "..."}.
    """
    g = StateGraph(dict)

    # Nodes (placeholders: worker calls real functions via AGENT_FUNCS)
    for name in [
        "booking",
        "scheduling",
        "pickup",
        "airline_checkin",
        "bagdrop",
        "flight_monitor",
        "destination_delivery",
        "routing",
        "pricing",
        "exceptions",
    ]:
        g.add_node(name, lambda s: s)

    g.set_entry_point("booking")

    # Phase-2 edges
    g.add_edge("booking", "scheduling")
    g.add_edge("scheduling", "pickup")
    g.add_edge("pickup", "airline_checkin")
    g.add_edge("airline_checkin", "bagdrop")
    g.add_edge("bagdrop", "flight_monitor")
    g.add_edge("flight_monitor", "destination_delivery")
    g.add_edge("destination_delivery", "routing")
    g.add_edge("routing", "pricing")
    g.add_edge("pricing", "exceptions")

    return g.compile()


AGENT_FUNCS = {
    "booking": booking_agent,
    "scheduling": scheduling_agent,
    "pickup": pickup_agent,
    "airline_checkin": airline_checkin_agent,
    "bagdrop": bagdrop_agent,
    "flight_monitor": flight_monitor_agent,
    "destination_delivery": destination_delivery_agent,
    "routing": routing_agent,
    "pricing": pricing_agent,
    "exceptions": exception_agent,
}
