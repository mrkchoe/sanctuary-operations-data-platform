import pytest

from app import create_app
from app.extensions import db
from app.models import User, UserRole


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_user(app):
    user = User(email="admin@example.com", role=UserRole.ADMIN)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def staff_user(app):
    user = User(email="staff@example.com", role=UserRole.STAFF)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email="staff@example.com", password="password123"):
    return client.post("/auth/login", data={"email": email, "password": password}, follow_redirects=True)
