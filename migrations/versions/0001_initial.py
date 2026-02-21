"""Initial schema.

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-03 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("admin", "staff", name="userrole"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "dogs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("estimated_age_years", sa.Float(), nullable=True),
        sa.Column("sex", sa.String(length=20), nullable=False),
        sa.Column("breed", sa.String(length=120), nullable=False),
        sa.Column("intake_date", sa.Date(), nullable=False),
        sa.Column("intake_source", sa.String(length=255), nullable=False),
        sa.Column("status", sa.Enum("INTAKE", "AVAILABLE", "FOSTER", "ADOPTED", "MEDICAL_HOLD", name="dogstatus"), nullable=False),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_dogs_status", "dogs", ["status"], unique=False)
    op.create_index("ix_dogs_intake_date", "dogs", ["intake_date"], unique=False)

    op.create_table(
        "care_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dog_id", sa.Integer(), sa.ForeignKey("dogs.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("type", sa.Enum("FEEDING", "WALK", "MEDS", "VET_VISIT", "TRAINING", "GROOMING", name="caretype"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_care_logs_dog_id", "care_logs", ["dog_id"], unique=False)
    op.create_index("ix_care_logs_date", "care_logs", ["date"], unique=False)

    op.create_table(
        "adoptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dog_id", sa.Integer(), sa.ForeignKey("dogs.id"), nullable=False),
        sa.Column("adopter_name", sa.String(length=120), nullable=False),
        sa.Column("adopter_email", sa.String(length=255), nullable=False),
        sa.Column("adopter_phone", sa.String(length=50), nullable=True),
        sa.Column("application_date", sa.Date(), nullable=False),
        sa.Column("decision_status", sa.Enum("PENDING", "APPROVED", "REJECTED", name="decisionstatus"), nullable=False),
        sa.Column("decision_date", sa.Date(), nullable=True),
        sa.Column("adoption_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_adoptions_dog_id", "adoptions", ["dog_id"], unique=False)
    op.create_index("ix_adoptions_decision_status", "adoptions", ["decision_status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_adoptions_decision_status", table_name="adoptions")
    op.drop_index("ix_adoptions_dog_id", table_name="adoptions")
    op.drop_table("adoptions")

    op.drop_index("ix_care_logs_date", table_name="care_logs")
    op.drop_index("ix_care_logs_dog_id", table_name="care_logs")
    op.drop_table("care_logs")

    op.drop_index("ix_dogs_intake_date", table_name="dogs")
    op.drop_index("ix_dogs_status", table_name="dogs")
    op.drop_table("dogs")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS dogstatus")
    op.execute("DROP TYPE IF EXISTS caretype")
    op.execute("DROP TYPE IF EXISTS decisionstatus")
