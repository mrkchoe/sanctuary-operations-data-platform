"""Add demo user for local testing.

Revision ID: 0002_add_demo_user
Revises: 0001_initial
Create Date: 2026-02-10

"""

from datetime import datetime
from alembic import op
import sqlalchemy as sa
from werkzeug.security import generate_password_hash

revision = "0002_add_demo_user"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

DEMO_EMAIL = "staff@example.com"
DEMO_PASSWORD = "demo1234"


def upgrade() -> None:
    conn = op.get_bind()
    # Only insert if no users exist (e.g. fresh DB)
    result = conn.execute(sa.text("SELECT COUNT(1) FROM users"))
    if result.scalar() != 0:
        return
    password_hash = generate_password_hash(DEMO_PASSWORD)
    created_at = datetime.utcnow()
    conn.execute(
        sa.text(
            "INSERT INTO users (email, password_hash, role, created_at) "
            "VALUES (:email, :password_hash, :role, :created_at)"
        ),
        {"email": DEMO_EMAIL, "password_hash": password_hash, "role": "staff", "created_at": created_at},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM users WHERE email = :email"), {"email": DEMO_EMAIL})
