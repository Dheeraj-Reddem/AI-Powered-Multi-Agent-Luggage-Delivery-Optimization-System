from app.models import AgentLog

def booking_agent(state, db):
    order = state["order"]

    decision = "Validated booking fields and initialized order workflow."
    reasoning = f"User={order.user_name}, flight={order.flight_number}, luggage_count={order.luggage_count}"

    db.add(AgentLog(
        order_id=order.order_id,
        agent_name="booking_agent",
        decision=decision,
        reasoning=reasoning,
        outcome="ok",
    ))
    state["status"] = "booking_confirmed"
    return state
