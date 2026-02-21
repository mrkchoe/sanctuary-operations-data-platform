"""BCNF: extract adopters into own table (email determines name/phone).

Revision ID: 0003_bcnf_adopters
Revises: 0002_add_demo_user
Create Date: 2026-02-10

"""

from alembic import op
import sqlalchemy as sa

revision = "0003_bcnf_adopters"
down_revision = "0002_add_demo_user"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    # 1. Create adopters table
    op.create_table(
        "adopters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_adopters_email", "adopters", ["email"], unique=True)

    # 2. Populate adopters from distinct adoption adopter_email (one row per email)
    conn.execute(
        sa.text(
            "INSERT INTO adopters (email, name, phone, created_at) "
            "SELECT adopter_email, adopter_name, adopter_phone, MIN(created_at) "
            "FROM adoptions GROUP BY adopter_email"
        )
    )

    # 3. SQLite: recreate adoptions with adopter_id; others: add column, backfill, drop old
    if conn.engine.name == "sqlite":
        op.create_table(
            "adoptions_new",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("dog_id", sa.Integer(), sa.ForeignKey("dogs.id"), nullable=False),
            sa.Column("adopter_id", sa.Integer(), sa.ForeignKey("adopters.id"), nullable=False),
            sa.Column("application_date", sa.Date(), nullable=False),
            sa.Column("decision_status", sa.Enum("PENDING", "APPROVED", "REJECTED", name="decisionstatus"), nullable=False),
            sa.Column("decision_date", sa.Date(), nullable=True),
            sa.Column("adoption_date", sa.Date(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        conn.execute(
            sa.text(
                "INSERT INTO adoptions_new (id, dog_id, adopter_id, application_date, decision_status, decision_date, adoption_date, notes, created_at) "
                "SELECT a.id, a.dog_id, b.id, a.application_date, a.decision_status, a.decision_date, a.adoption_date, a.notes, a.created_at "
                "FROM adoptions a JOIN adopters b ON b.email = a.adopter_email"
            )
        )
        op.drop_table("adoptions")
        op.rename_table("adoptions_new", "adoptions")
        op.create_index("ix_adoptions_dog_id", "adoptions", ["dog_id"], unique=False)
        op.create_index("ix_adoptions_decision_status", "adoptions", ["decision_status"], unique=False)
        op.create_index("ix_adoptions_adopter_id", "adoptions", ["adopter_id"], unique=False)
    else:
        op.add_column("adoptions", sa.Column("adopter_id", sa.Integer(), sa.ForeignKey("adopters.id"), nullable=True))
        conn.execute(
            sa.text(
                "UPDATE adoptions SET adopter_id = (SELECT id FROM adopters WHERE adopters.email = adoptions.adopter_email)"
            )
        )
        op.alter_column("adoptions", "adopter_id", nullable=False)
        op.create_index("ix_adoptions_adopter_id", "adoptions", ["adopter_id"], unique=False)
        op.drop_column("adoptions", "adopter_name")
        op.drop_column("adoptions", "adopter_email")
        op.drop_column("adoptions", "adopter_phone")


def downgrade() -> None:
    conn = op.get_bind()
    if conn.engine.name == "sqlite":
        op.create_table(
            "adoptions_old",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("dog_id", sa.Integer(), sa.ForeignKey("dogs.id"), nullable=False),
            sa.Column("adopter_name", sa.String(120), nullable=False),
            sa.Column("adopter_email", sa.String(255), nullable=False),
            sa.Column("adopter_phone", sa.String(50), nullable=True),
            sa.Column("application_date", sa.Date(), nullable=False),
            sa.Column("decision_status", sa.Enum("PENDING", "APPROVED", "REJECTED", name="decisionstatus"), nullable=False),
            sa.Column("decision_date", sa.Date(), nullable=True),
            sa.Column("adoption_date", sa.Date(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        conn.execute(
            sa.text(
                "INSERT INTO adoptions_old (id, dog_id, adopter_name, adopter_email, adopter_phone, application_date, decision_status, decision_date, adoption_date, notes, created_at) "
                "SELECT a.id, a.dog_id, b.name, b.email, b.phone, a.application_date, a.decision_status, a.decision_date, a.adoption_date, a.notes, a.created_at "
                "FROM adoptions a JOIN adopters b ON b.id = a.adopter_id"
            )
        )
        op.drop_table("adoptions")
        op.rename_table("adoptions_old", "adoptions")
        op.create_index("ix_adoptions_dog_id", "adoptions", ["dog_id"], unique=False)
        op.create_index("ix_adoptions_decision_status", "adoptions", ["decision_status"], unique=False)
    else:
        op.add_column("adoptions", sa.Column("adopter_name", sa.String(120), nullable=True))
        op.add_column("adoptions", sa.Column("adopter_email", sa.String(255), nullable=True))
        op.add_column("adoptions", sa.Column("adopter_phone", sa.String(50), nullable=True))
        conn.execute(
            sa.text(
                "UPDATE adoptions SET adopter_name = (SELECT name FROM adopters WHERE adopters.id = adoptions.adopter_id), "
                "adopter_email = (SELECT email FROM adopters WHERE adopters.id = adoptions.adopter_id), "
                "adopter_phone = (SELECT phone FROM adopters WHERE adopters.id = adoptions.adopter_id)"
            )
        )
        op.alter_column("adoptions", "adopter_name", nullable=False)
        op.alter_column("adoptions", "adopter_email", nullable=False)
        op.drop_index("ix_adoptions_adopter_id", table_name="adoptions")
        op.drop_column("adoptions", "adopter_id")
    op.drop_index("ix_adopters_email", table_name="adopters")
    op.drop_table("adopters")