import json
from celery import Celery
from sqlalchemy.orm import Session

from app.settings import settings
from app.db import SessionLocal
from app.models import Order
from app.orchestrator import AGENT_FUNCS

celery = Celery(
    "luggage_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

@celery.task(bind=True)
def process_order(self, order_id: str):
    db: Session = SessionLocal()
    try:
        order = db.get(Order, order_id)

        # ✅ 1) must check order exists first
        if not order:
            return {"error": "order_not_found", "order_id": order_id}

        # ✅ 2) idempotency: don’t re-run completed/failed orders
        if order.status in {"delivered", "failed"}:
            return {"ok": True, "skipped": True, "status": order.status}

        # ✅ Phase-2 sequence (edit to match what you actually implemented)
        node_sequence = [
            "booking",
            "pickup",
            "airline_checkin",
            "bagdrop",
            "flight_monitor",
            "destination_delivery",
            "pricing",
            "exceptions",
        ]

        state = {"order": order, "status": order.status or "initiated"}

        for node_name in node_sequence:
            fn = AGENT_FUNCS.get(node_name)
            if not fn:
                # If you haven’t implemented one yet, skip safely.
                continue

            state = fn(state, db)
            db.commit()
            db.refresh(order)

            # ✅ optional: stop early if something failed
            if order.status == "failed":
                break

        # Save summary json (useful for UI)
        result = {
            "order_id": order.order_id,
            "status": order.status,
            "airline_integration_status": getattr(order, "airline_integration_status", None),
            "pickup_time_iso": order.pickup_time_iso,
            "eta_to_airport_minutes": order.eta_to_airport_minutes,
            "distance_km": order.distance_km,
            "total_price": order.total_price,
            "destination_address": getattr(order, "destination_address", None),
        }

        order.agent_result_json = json.dumps(result)
        db.commit()

        return result

    except Exception as e:
        db.rollback()
        try:
            order = db.get(Order, order_id)
            if order:
                order.status = "failed"
                db.commit()
        except Exception:
            pass
        return {"error": "workflow_failed", "details": str(e), "order_id": order_id}

    finally:
        db.close()
