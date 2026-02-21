from app.models import User, UserRole
from tests.conftest import login


def test_register_login_logout(client):
    response = client.post(
        "/auth/register",
        data={"email": "new@example.com", "password": "password123", "confirm_password": "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    user = User.query.filter_by(email="new@example.com").first()
    assert user is not None
    assert user.role == UserRole.STAFF

    response = login(client, email="new@example.com", password="password123")
    assert b"Dogs" in response.data

    response = client.get("/auth/logout", follow_redirects=True)
    assert b"logged out" in response.data.lower()


def test_protected_requires_login(client):
    response = client.get("/dogs/", follow_redirects=True)
    assert b"Sign in" in response.data or b"Login" in response.data
