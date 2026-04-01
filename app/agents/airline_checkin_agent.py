import asyncio
from app.models import AgentLog, Passenger, AirlineCheckin, BagDrop, Bag
from app.airline_integrations import get_adapter_for_airline

def airline_code_from_flight(flight_number: str) -> str:
    # "UA123" -> "UA"
    return "".join([c for c in flight_number if c.isalpha()])[:3].upper() or "XX"

def airline_checkin_agent(state, db):
    order = state["order"]

    # eligibility rule (simple for now)
    # You can add: supported airports, domestic only, time windows, etc.
    airline_code = airline_code_from_flight(order.flight_number)

    passenger = db.query(Passenger).filter(Passenger.order_id == order.order_id).first()
    if not passenger:
        raise RuntimeError("Passenger record missing")

    # create / get checkin row
    checkin = db.query(AirlineCheckin).filter(AirlineCheckin.order_id == order.order_id).first()
    if not checkin:
        checkin = AirlineCheckin(
            order_id=order.order_id,
            airline_code=airline_code,
            flight_number=order.flight_number,
            status="not_started",
        )
        db.add(checkin)
        db.commit()
        db.refresh(checkin)

    adapter = get_adapter_for_airline(airline_code)

    # Call async adapter from sync agent (simple approach)
    res = asyncio.run(adapter.check_in(
        airline_code=airline_code,
        flight_number=order.flight_number,
        pnr=passenger.pnr,
        last_name=passenger.last_name
    ))

    if res.status == "success":
        checkin.status = "success"
        checkin.confirmation_code = res.confirmation_code
        checkin.boarding_pass_url = res.boarding_pass_url
        checkin.error_message = None
        order.airline_integration_status = "checked_in"
        order.status = "checked_in"
        outcome = "ok"
        decision = f"Airline check-in success: confirmation={res.confirmation_code}"
    else:
        checkin.status = "failed"
        checkin.error_message = res.error_message or "unknown_error"
        order.airline_integration_status = "checkin_failed"
        order.status = "needs_manual_checkin"
        outcome = "needs_manual"
        decision = f"Airline check-in failed: {checkin.error_message}"

    db.add(AgentLog(
        order_id=order.order_id,
        agent_name="airline_checkin_agent",
        decision=decision,
        reasoning=f"Used adapter for airline_code={airline_code}.",
        outcome=outcome
    ))
    db.commit()

    # If check-in succeeded, schedule bag drop
    if checkin.status == "success":
        bd = db.query(BagDrop).filter(BagDrop.order_id == order.order_id).first()
        if not bd:
            bd = BagDrop(order_id=order.order_id)
            db.add(bd)
            db.commit()
            db.refresh(bd)

        bd_res = asyncio.run(adapter.schedule_bag_drop(
            airline_code=airline_code,
            flight_number=order.flight_number,
            pnr=passenger.pnr
        ))

        if bd_res.status == "scheduled":
            bd.status = "scheduled"
            bd.facility = bd_res.facility
            bd.appointment_time_iso = bd_res.appointment_time_iso
            order.airline_integration_status = "bagdrop_scheduled"
            order.status = "bagdrop_scheduled"
            db.add(AgentLog(
                order_id=order.order_id,
                agent_name="bagdrop_agent",
                decision=f"Bag drop scheduled at {bd.facility}",
                reasoning="Partner scheduling flow (mock adapter for now).",
                outcome="ok"
            ))
        else:
            bd.status = "failed"
            order.status = "needs_manual_bagdrop"
            db.add(AgentLog(
                order_id=order.order_id,
                agent_name="bagdrop_agent",
                decision=f"Bag drop scheduling failed: {bd_res.error_message}",
                reasoning="Partner scheduling failed; fallback required.",
                outcome="needs_manual"
            ))

        db.commit()

    state["status"] = order.status
    return state