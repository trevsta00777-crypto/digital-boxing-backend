from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.models import Payment, PaymentStatus


def _create_priced_event(client, auth_headers):
    r = client.post(
        "/events",
        json={
            "name": "Ticketed Night",
            "event_date": (datetime.utcnow() + timedelta(days=10)).isoformat(),
            "ticket_price_cents": 2500,
            "currency": "usd",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


class TestPayments:
    def test_checkout_requires_auth(self, client):
        r = client.post("/payments/checkout", json={"event_id": 1, "quantity": 1})
        assert r.status_code in (401, 403)

    @patch("app.routes.payments.stripe.checkout.Session.create")
    def test_create_checkout_mocked(self, mock_create, client, auth_headers, db):
        event_id = _create_priced_event(client, auth_headers)
        mock_session = MagicMock()
        mock_session.id = "cs_test_123"
        mock_session.url = "https://checkout.stripe.com/test"
        mock_create.return_value = mock_session

        r = client.post(
            "/payments/checkout",
            json={"event_id": event_id, "quantity": 2},
            headers=auth_headers,
        )
        assert r.status_code == 201
        body = r.json()
        assert body["session_id"] == "cs_test_123"
        assert body["checkout_url"].startswith("https://")
        payment = db.query(Payment).filter(Payment.id == body["payment_id"]).first()
        assert payment is not None
        assert payment.amount_cents == 5000
        assert payment.status == PaymentStatus.PENDING.value

    @patch("app.routes.payments.stripe.Webhook.construct_event")
    def test_webhook_marks_completed(self, mock_construct, client, auth_headers, db):
        event_id = _create_priced_event(client, auth_headers)
        with patch("app.routes.payments.stripe.checkout.Session.create") as mock_create:
            mock_session = MagicMock()
            mock_session.id = "cs_test_wh"
            mock_session.url = "https://checkout.stripe.com/test"
            mock_create.return_value = mock_session
            r = client.post(
                "/payments/checkout",
                json={"event_id": event_id, "quantity": 1},
                headers=auth_headers,
            )
            payment_id = r.json()["payment_id"]

        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_wh",
                    "payment_intent": "pi_test",
                    "customer": "cus_test",
                }
            },
        }
        wh = client.post(
            "/payments/webhook",
            data=b"{}",
            headers={"Stripe-Signature": "t=1,v1=fake"},
        )
        assert wh.status_code == 200
        db.expire_all()
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        assert payment.status == PaymentStatus.COMPLETED.value
