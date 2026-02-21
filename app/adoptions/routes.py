from flask import flash, redirect, render_template, url_for
from flask_login import login_required

from app.adoptions import adoptions_bp
from app.adoptions.forms import AdoptionForm
from app.extensions import db
from app.models import Adopter, Adoption, DecisionStatus, Dog, DogStatus


@adoptions_bp.before_request
@login_required
def require_login():
    return None


def _get_or_create_adopter(email: str, name: str, phone: str | None) -> Adopter:
    email = email.lower().strip()
    adopter = Adopter.query.filter_by(email=email).first()
    if adopter:
        adopter.name = name
        adopter.phone = phone or adopter.phone
        return adopter
    return Adopter(email=email, name=name, phone=phone or None)


@adoptions_bp.route("/dogs/<int:dog_id>/new", methods=["GET", "POST"])
def new_adoption(dog_id: int):
    dog = Dog.query.filter(Dog.id == dog_id, Dog.archived_at.is_(None)).first_or_404()
    form = AdoptionForm()
    if form.validate_on_submit():
        adopter = _get_or_create_adopter(
            form.adopter_email.data,
            form.adopter_name.data,
            form.adopter_phone.data,
        )
        db.session.add(adopter)
        db.session.flush()
        adoption = Adoption(
            dog_id=dog.id,
            adopter_id=adopter.id,
            application_date=form.application_date.data,
            decision_status=DecisionStatus(form.decision_status.data),
            decision_date=form.decision_date.data,
            adoption_date=form.adoption_date.data,
            notes=form.notes.data,
        )
        if adoption.decision_status == DecisionStatus.APPROVED:
            dog.status = DogStatus.ADOPTED
        db.session.add(adoption)
        db.session.commit()
        flash("Adoption application created.", "success")
        return redirect(url_for("dogs.detail", dog_id=dog.id))
    return render_template("adoptions/new.html", form=form, dog=dog)


@adoptions_bp.route("/<int:adoption_id>/edit", methods=["GET", "POST"])
def edit_adoption(adoption_id: int):
    adoption = Adoption.query.get_or_404(adoption_id)
    dog = adoption.dog
    if dog.archived_at:
        flash("Archived dogs cannot be edited.", "warning")
        return redirect(url_for("dogs.list_dogs"))
    form = AdoptionForm()
    if form.validate_on_submit():
        adopter = _get_or_create_adopter(
            form.adopter_email.data,
            form.adopter_name.data,
            form.adopter_phone.data,
        )
        db.session.add(adopter)
        db.session.flush()
        adoption.adopter_id = adopter.id
        adoption.application_date = form.application_date.data
        adoption.decision_status = DecisionStatus(form.decision_status.data)
        adoption.decision_date = form.decision_date.data
        adoption.adoption_date = form.adoption_date.data
        adoption.notes = form.notes.data
        if adoption.decision_status == DecisionStatus.APPROVED and adoption.adoption_date:
            dog.status = DogStatus.ADOPTED
        db.session.commit()
        flash("Adoption updated.", "success")
        return redirect(url_for("dogs.detail", dog_id=dog.id))
    # Prefill from adoption and adopter
    form.adopter_name.data = adoption.adopter.name
    form.adopter_email.data = adoption.adopter.email
    form.adopter_phone.data = adoption.adopter.phone or ""
    form.application_date.data = adoption.application_date
    form.decision_status.data = adoption.decision_status.value
    form.decision_date.data = adoption.decision_date
    form.adoption_date.data = adoption.adoption_date
    form.notes.data = adoption.notes
    return render_template("adoptions/edit.html", form=form, dog=dog, adoption=adoption)
