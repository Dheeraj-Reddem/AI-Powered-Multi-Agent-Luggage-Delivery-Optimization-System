from app.models import AgentLog
from app.settings import settings

def pricing_agent(state, db):
    order = state["order"]

    distance_km = order.distance_km or 0.0
    weight = order.luggage_weight_kg or 0.0

    price = settings.BASE_PRICE + (settings.PRICE_PER_KM * distance_km) + (settings.PRICE_PER_KG * weight)
    price = round(float(price), 2)

    order.total_price = price
    order.status = "priced"

    db.add(AgentLog(
        order_id=order.order_id,
        agent_name="pricing_agent",
        decision=f"total_price={order.total_price}",
        reasoning=f"BASE({settings.BASE_PRICE}) + KM({settings.PRICE_PER_KM}*{distance_km}) + KG({settings.PRICE_PER_KG}*{weight})",
        outcome="ok"
    ))

    state["status"] = "priced"
    return state
