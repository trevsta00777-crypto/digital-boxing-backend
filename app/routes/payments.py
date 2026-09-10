"""Stripe Checkout for event tickets + webhook verification.

Subscription support is a light stub (Checkout subscription mode).
"""
from __future__ import annotations

import json
from typing import Optional

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models import Event, Payment, PaymentStatus, PaymentType, User
from app.schemas import (
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    PaymentResponse,
    SubscriptionStubCreate,
)

router = APIRouter(prefix="/payments", tags=["payments"])


def _configure_stripe() -> None:
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=503,
            detail="Stripe is not configured (set STRIPE_SECRET_KEY)",
        )
    stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post(
    "/checkout",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_checkout_session(
    body: CheckoutSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout Session for event tickets."""
    _configure_stripe()
    event = db.query(Event).filter(Event.id == body.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.ticket_price_cents <= 0:
        raise HTTPException(
            status_code=400,
            detail="Event has no ticket price configured",
        )

    amount = event.ticket_price_cents * body.quantity
    payment = Payment(
        user_id=current_user.id,
        event_id=event.id,
        payment_type=PaymentType.EVENT_TICKET.value,
        amount_cents=amount,
        currency=event.currency or "usd",
        status=PaymentStatus.PENDING.value,
        metadata_json=json.dumps({"quantity": body.quantity}),
    )
    db.add(payment)
    db.flush()

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            success_url=settings.STRIPE_SUCCESS_URL
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.STRIPE_CANCEL_URL,
            line_items=[
                {
                    "price_data": {
                        "currency": payment.currency,
                        "unit_amount": event.ticket_price_cents,
                        "product_data": {
                            "name": f"Ticket: {event.name}",
                            "description": event.description or "Event ticket",
                        },
                    },
                    "quantity": body.quantity,
                }
            ],
            metadata={
                "payment_id": str(payment.id),
                "event_id": str(event.id),
                "user_id": str(current_user.id),
            },
            client_reference_id=str(payment.id),
        )
    except stripe.error.StripeError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"Stripe error: {exc.user_message or str(exc)}") from exc

    payment.stripe_checkout_session_id = session.id
    db.commit()
    db.refresh(payment)

    return CheckoutSessionResponse(
        checkout_url=session.url or "",
        session_id=session.id,
        payment_id=payment.id,
    )


@router.post(
    "/subscription/checkout",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subscription_checkout(
    body: SubscriptionStubCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Light stub: Stripe Checkout in subscription mode."""
    _configure_stripe()
    price_id = body.price_id or settings.STRIPE_SUBSCRIPTION_PRICE_ID
    if not price_id:
        raise HTTPException(
            status_code=400,
            detail="Set price_id or STRIPE_SUBSCRIPTION_PRICE_ID",
        )

    payment = Payment(
        user_id=current_user.id,
        event_id=None,
        payment_type=PaymentType.SUBSCRIPTION.value,
        amount_cents=0,
        currency="usd",
        status=PaymentStatus.PENDING.value,
        metadata_json=json.dumps({"price_id": price_id}),
    )
    db.add(payment)
    db.flush()

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            success_url=settings.STRIPE_SUCCESS_URL
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.STRIPE_CANCEL_URL,
            line_items=[{"price": price_id, "quantity": 1}],
            metadata={
                "payment_id": str(payment.id),
                "user_id": str(current_user.id),
                "type": "subscription",
            },
            client_reference_id=str(payment.id),
        )
    except stripe.error.StripeError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"Stripe error: {exc.user_message or str(exc)}") from exc

    payment.stripe_checkout_session_id = session.id
    db.commit()
    db.refresh(payment)
    return CheckoutSessionResponse(
        checkout_url=session.url or "",
        session_id=session.id,
        payment_id=payment.id,
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
):
    """Verify Stripe webhook signature and update Payment rows."""
    payload = await request.body()
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid payload") from exc
    except stripe.error.SignatureVerificationError as exc:
        raise HTTPException(status_code=400, detail="Invalid signature") from exc

    etype = event["type"]
    data_object = event["data"]["object"]

    if etype == "checkout.session.completed":
        session_id = data_object.get("id")
        payment = (
            db.query(Payment)
            .filter(Payment.stripe_checkout_session_id == session_id)
            .first()
        )
        if payment:
            payment.status = PaymentStatus.COMPLETED.value
            payment.stripe_payment_intent_id = data_object.get("payment_intent")
            payment.stripe_customer_id = data_object.get("customer")
            db.commit()
    elif etype in {"checkout.session.expired", "payment_intent.payment_failed"}:
        session_id = data_object.get("id")
        # payment_intent failures may not have checkout session id
        payment = None
        if session_id:
            payment = (
                db.query(Payment)
                .filter(Payment.stripe_checkout_session_id == session_id)
                .first()
            )
        if not payment and data_object.get("id"):
            payment = (
                db.query(Payment)
                .filter(Payment.stripe_payment_intent_id == data_object.get("id"))
                .first()
            )
        if payment:
            payment.status = PaymentStatus.FAILED.value
            db.commit()

    return {"received": True}


@router.get("/me", response_model=list[PaymentResponse])
def list_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )
