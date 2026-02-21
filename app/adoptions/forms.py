from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, TextAreaField
from wtforms.validators import Email, InputRequired, Optional, ValidationError

from app.models import DecisionStatus


class AdoptionForm(FlaskForm):
    adopter_name = StringField("Adopter Name", validators=[InputRequired()])
    adopter_email = StringField("Adopter Email", validators=[InputRequired(), Email()])
    adopter_phone = StringField("Adopter Phone", validators=[Optional()])
    application_date = DateField("Application Date", validators=[InputRequired()], default=date.today)
    decision_status = SelectField(
        "Decision Status",
        choices=[(status.value, status.value) for status in DecisionStatus],
        validators=[InputRequired()],
    )
    decision_date = DateField("Decision Date", validators=[Optional()])
    adoption_date = DateField("Adoption Date", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])

    def validate_decision_date(self, field):
        if self.decision_status.data in {DecisionStatus.APPROVED.value, DecisionStatus.REJECTED.value}:
            if not field.data:
                raise ValidationError("Decision date is required when a decision is made.")

    def validate_adoption_date(self, field):
        if self.decision_status.data == DecisionStatus.APPROVED.value and not field.data:
            raise ValidationError("Adoption date is required when approved.")
