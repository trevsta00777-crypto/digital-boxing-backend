from datetime import datetime, timedelta


class TestHealth:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "version" in body

    def test_security_headers(self, client):
        response = client.get("/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"


class TestAuth:
    def test_register_user(self, client):
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepass123",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        assert response.json()["email"] == "newuser@example.com"

    def test_register_duplicate_email(self, client, test_user):
        response = client.post(
            "/auth/register",
            json={
                "email": test_user.email,
                "username": "anotheruser",
                "password": "pass12345",
                "full_name": "Another User",
            },
        )
        assert response.status_code == 400

    def test_login(self, client, test_user):
        response = client.post(
            "/auth/login",
            json={"email": test_user.email, "password": "testpass123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_invalid_password(self, client, test_user):
        response = client.post(
            "/auth/login",
            json={"email": test_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_me(self, client, auth_headers):
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"


class TestFighters:
    def test_create_fighter(self, client, auth_headers):
        response = client.post(
            "/fighters",
            json={
                "name": "Muhammad Ali",
                "nickname": "The Greatest",
                "weight_class": "Heavyweight",
                "height": 6.37,
                "reach": 6.75,
                "bio": "Legendary boxer",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Muhammad Ali"

    def test_list_fighters(self, client):
        response = client.get("/fighters")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestEventsAndMatches:
    def test_create_event_and_match(self, client, auth_headers):
        ev = client.post(
            "/events",
            json={
                "name": "Fight Night",
                "description": "Card 1",
                "location": "Melbourne",
                "event_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "ticket_price_cents": 5000,
                "currency": "usd",
            },
            headers=auth_headers,
        )
        assert ev.status_code == 201
        event_id = ev.json()["id"]

        f1 = client.post(
            "/fighters",
            json={"name": "A", "weight_class": "Lightweight"},
            headers=auth_headers,
        )
        f2 = client.post(
            "/fighters",
            json={"name": "B", "weight_class": "Lightweight"},
            headers=auth_headers,
        )
        assert f1.status_code == 201 and f2.status_code == 201

        m = client.post(
            "/matches",
            json={
                "fighter1_id": f1.json()["id"],
                "fighter2_id": f2.json()["id"],
                "event_id": event_id,
                "rounds": 12,
                "match_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            },
            headers=auth_headers,
        )
        assert m.status_code == 201
