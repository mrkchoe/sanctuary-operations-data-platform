from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.care import care_bp
from app.care.forms import CareLogForm
from app.extensions import db
from app.models import CareLog, CareType, Dog


@care_bp.before_request
@login_required
def require_login():
    return None


@care_bp.route("/dogs/<int:dog_id>/new", methods=["GET", "POST"])
def new_log(dog_id: int):
    dog = Dog.query.filter(Dog.id == dog_id, Dog.archived_at.is_(None)).first_or_404()
    form = CareLogForm()
    if form.validate_on_submit():
        log = CareLog(
            dog_id=dog.id,
            user_id=current_user.id,
            date=form.date.data,
            type=CareType(form.type.data),
            notes=form.notes.data,
            cost=form.cost.data,
        )
        db.session.add(log)
        db.session.commit()
        flash("Care log added.", "success")
        return redirect(url_for("dogs.detail", dog_id=dog.id))
    return render_template("care/new.html", form=form, dog=dog)
