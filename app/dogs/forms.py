from datetime import date
from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from app.models import DogStatus


class DogForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(max=120)])
    estimated_age_years = StringField("Estimated Age (years)", validators=[Optional()])
    sex = SelectField(
        "Sex",
        choices=[("Male", "Male"), ("Female", "Female"), ("Unknown", "Unknown")],
        validators=[InputRequired()],
    )
    breed = StringField("Breed", validators=[InputRequired(), Length(max=120)])
    intake_date = DateField("Intake Date", validators=[InputRequired()], default=date.today)
    intake_source = StringField("Intake Source", validators=[InputRequired(), Length(max=255)])
    status = SelectField(
        "Status",
        choices=[(status.value, status.value) for status in DogStatus],
        validators=[InputRequired()],
    )

    def validate_estimated_age_years(self, field):
        if not field.data:
            return
        try:
            value = Decimal(field.data)
        except Exception as exc:  # pragma: no cover - validation
            raise ValidationError("Estimated age must be a number.") from exc
        if value < 0:
            raise ValidationError("Estimated age must be non-negative.")
