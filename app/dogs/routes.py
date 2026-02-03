from datetime import date, datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from app.dogs import dogs_bp
from app.dogs.forms import DogForm
from app.extensions import db
from app.models import Dog, DogStatus


@dogs_bp.before_request
@login_required
def require_login():
    return None


@dogs_bp.route("/", methods=["GET"])
def list_dogs():
    status = request.args.get("status")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    search = request.args.get("search", "").strip()

    query = Dog.query.filter(Dog.archived_at.is_(None))

    if status:
        try:
            query = query.filter(Dog.status == DogStatus(status))
        except ValueError:
            status = None
    if start_date:
        try:
            query = query.filter(Dog.intake_date >= date.fromisoformat(start_date))
        except ValueError:
            start_date = None
    if end_date:
        try:
            query = query.filter(Dog.intake_date <= date.fromisoformat(end_date))
        except ValueError:
            end_date = None
    if search:
        like_value = f"%{search}%"
        query = query.filter(or_(Dog.name.ilike(like_value), Dog.breed.ilike(like_value)))

    dogs = query.order_by(Dog.intake_date.desc()).all()
    return render_template(
        "dogs/list.html",
        dogs=dogs,
        filters={"status": status, "start_date": start_date, "end_date": end_date, "search": search},
        statuses=[status.value for status in DogStatus],
    )


@dogs_bp.route("/new", methods=["GET", "POST"])
def new_dog():
    form = DogForm()
    if form.validate_on_submit():
        estimated_age = float(form.estimated_age_years.data) if form.estimated_age_years.data else None
        dog = Dog(
            name=form.name.data,
            estimated_age_years=estimated_age,
            sex=form.sex.data,
            breed=form.breed.data,
            intake_date=form.intake_date.data,
            intake_source=form.intake_source.data,
            status=DogStatus(form.status.data),
        )
        db.session.add(dog)
        db.session.commit()
        flash("Dog intake created.", "success")
        return redirect(url_for("dogs.detail", dog_id=dog.id))
    return render_template("dogs/new.html", form=form)


@dogs_bp.route("/<int:dog_id>", methods=["GET"])
def detail(dog_id: int):
    dog = Dog.query.filter(Dog.id == dog_id, Dog.archived_at.is_(None)).first_or_404()

    start = request.args.get("cost_start")
    end = request.args.get("cost_end")
    try:
        start_date = date.fromisoformat(start) if start else None
    except ValueError:
        start_date = None
    try:
        end_date = date.fromisoformat(end) if end else None
    except ValueError:
        end_date = None
    total_cost = dog.total_cost(start_date=start_date, end_date=end_date)

    care_logs = (
        dog.care_logs
        if not dog.care_logs
        else sorted(dog.care_logs, key=lambda log: log.date, reverse=True)
    )

    return render_template(
        "dogs/detail.html",
        dog=dog,
        care_logs=care_logs,
        total_cost=total_cost,
        cost_filters={"start": start, "end": end},
    )


@dogs_bp.route("/<int:dog_id>/edit", methods=["GET", "POST"])
def edit_dog(dog_id: int):
    dog = Dog.query.filter(Dog.id == dog_id, Dog.archived_at.is_(None)).first_or_404()
    form = DogForm(obj=dog)
    if form.validate_on_submit():
        dog.name = form.name.data
        dog.estimated_age_years = (
            float(form.estimated_age_years.data) if form.estimated_age_years.data else None
        )
        dog.sex = form.sex.data
        dog.breed = form.breed.data
        dog.intake_date = form.intake_date.data
        dog.intake_source = form.intake_source.data
        dog.status = DogStatus(form.status.data)
        db.session.commit()
        flash("Dog updated.", "success")
        return redirect(url_for("dogs.detail", dog_id=dog.id))
    return render_template("dogs/edit.html", form=form, dog=dog)


@dogs_bp.route("/<int:dog_id>/archive", methods=["POST"])
def archive_dog(dog_id: int):
    dog = Dog.query.filter(Dog.id == dog_id, Dog.archived_at.is_(None)).first_or_404()
    dog.archive()
    db.session.commit()
    flash("Dog archived.", "warning")
    return redirect(url_for("dogs.list_dogs"))
