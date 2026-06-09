import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import User
from app.security import hash_password, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def test_user():
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password("testpass123"),
        full_name="Test User"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()

@pytest.fixture
def test_token(test_user):
    return create_access_token(data={"sub": test_user.email})

class TestAuth:
    def test_register_user(self):
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepass123",
                "full_name": "New User"
            }
        )
        assert response.status_code == 201
        assert response.json()["email"] == "newuser@example.com"

    def test_register_duplicate_email(self, test_user):
        response = client.post(
            "/auth/register",
            json={
                "email": test_user.email,
                "username": "anotheruser",
                "password": "pass123",
                "full_name": "Another User"
            }
        )
        assert response.status_code == 400

    def test_login(self, test_user):
        response = client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_invalid_password(self, test_user):
        response = client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

class TestFighters:
    def test_create_fighter(self, test_token):
        response = client.post(
            "/fighters",
            json={
                "name": "Muhammad Ali",
                "nickname": "The Greatest",
                "weight_class": "Heavyweight",
                "height": 6.37,
                "reach": 6.75,
                "bio": "Legendary boxer"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Muhammad Ali"

    def test_list_fighters(self):
        response = client.get("/fighters")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

class TestHealth:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
