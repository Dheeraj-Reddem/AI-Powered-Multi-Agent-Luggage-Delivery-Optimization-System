from app.models import AgentLog

def exception_agent(state, db):
    # Placeholder: later you’ll use flight status API / courier events
    order = state["order"]

    db.add(AgentLog(
        order_id=order.order_id,
        agent_name="exception_agent",
        decision="No exceptions detected.",
        reasoning="MVP: no external event signals yet.",
        outcome="ok",
    ))
    return state
