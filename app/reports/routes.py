from datetime import date, timedelta

from flask import render_template
from flask_login import login_required
from sqlalchemy import func

from app.extensions import db
from app.models import CareLog, Dog, Adoption
from app.reports import reports_bp


@reports_bp.before_request
@login_required
def require_login():
    return None


def month_bucket(column):
    if db.engine.name == "sqlite":
        return func.strftime("%Y-%m", column)
    return func.to_char(column, "YYYY-MM")


@reports_bp.route("/", methods=["GET"])
def index():
    dogs_by_status = (
        db.session.query(Dog.status, func.count(Dog.id))
        .filter(Dog.archived_at.is_(None))
        .group_by(Dog.status)
        .all()
    )

    monthly_intakes = (
        db.session.query(month_bucket(Dog.intake_date).label("month"), func.count(Dog.id))
        .filter(Dog.archived_at.is_(None))
        .group_by("month")
        .order_by("month")
        .all()
    )

    monthly_adoptions = (
        db.session.query(month_bucket(Adoption.adoption_date).label("month"), func.count(Adoption.id))
        .join(Dog, Dog.id == Adoption.dog_id)
        .filter(Dog.archived_at.is_(None), Adoption.adoption_date.is_not(None))
        .group_by("month")
        .order_by("month")
        .all()
    )

    monthly_care_costs = (
        db.session.query(month_bucket(CareLog.date).label("month"), func.coalesce(func.sum(CareLog.cost), 0))
        .join(Dog, Dog.id == CareLog.dog_id)
        .filter(Dog.archived_at.is_(None), CareLog.cost.is_not(None))
        .group_by("month")
        .order_by("month")
        .all()
    )

    since_date = date.today() - timedelta(days=90)
    top_dogs = (
        db.session.query(Dog.name, func.coalesce(func.sum(CareLog.cost), 0).label("total_cost"))
        .join(CareLog, CareLog.dog_id == Dog.id)
        .filter(Dog.archived_at.is_(None), CareLog.cost.is_not(None), CareLog.date >= since_date)
        .group_by(Dog.id, Dog.name)
        .order_by(func.sum(CareLog.cost).desc())
        .limit(10)
        .all()
    )

    return render_template(
        "reports/index.html",
        dogs_by_status=dogs_by_status,
        monthly_intakes=monthly_intakes,
        monthly_adoptions=monthly_adoptions,
        monthly_care_costs=monthly_care_costs,
        top_dogs=top_dogs,
    )
