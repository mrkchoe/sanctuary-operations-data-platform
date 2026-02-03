from datetime import date
from decimal import Decimal, InvalidOperation

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Optional, ValidationError

from app.models import CareType


class CareLogForm(FlaskForm):
    date = DateField("Date", validators=[InputRequired()], default=date.today)
    type = SelectField(
        "Type",
        choices=[(care_type.value, care_type.value) for care_type in CareType],
        validators=[InputRequired()],
    )
    notes = TextAreaField("Notes", validators=[Optional()])
    cost = DecimalField("Cost", validators=[Optional()], places=2)

    def validate_cost(self, field):
        if field.data is None:
            return
        try:
            value = Decimal(field.data)
        except (InvalidOperation, TypeError) as exc:  # pragma: no cover - validation
            raise ValidationError("Cost must be a valid amount.") from exc
        if value < 0:
            raise ValidationError("Cost must be non-negative.")
