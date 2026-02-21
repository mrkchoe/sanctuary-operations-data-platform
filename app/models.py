import enum
from datetime import datetime, date
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"


class DogStatus(str, enum.Enum):
    INTAKE = "INTAKE"
    AVAILABLE = "AVAILABLE"
    FOSTER = "FOSTER"
    ADOPTED = "ADOPTED"
    MEDICAL_HOLD = "MEDICAL_HOLD"


class CareType(str, enum.Enum):
    FEEDING = "FEEDING"
    WALK = "WALK"
    MEDS = "MEDS"
    VET_VISIT = "VET_VISIT"
    TRAINING = "TRAINING"
    GROOMING = "GROOMING"


class DecisionStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STAFF)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    care_logs = db.relationship("CareLog", back_populates="user", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


class Dog(db.Model):
    __tablename__ = "dogs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    estimated_age_years = db.Column(db.Float, nullable=True)
    sex = db.Column(db.String(20), nullable=False)
    breed = db.Column(db.String(120), nullable=False)
    intake_date = db.Column(db.Date, nullable=False)
    intake_source = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(DogStatus), nullable=False, index=True)
    archived_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    care_logs = db.relationship("CareLog", back_populates="dog", lazy=True)
    adoptions = db.relationship("Adoption", back_populates="dog", lazy=True)

    def archive(self) -> None:
        self.archived_at = datetime.utcnow()

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None

    def total_cost(self, start_date: date | None = None, end_date: date | None = None) -> Decimal:
        query = (
            db.session.query(db.func.coalesce(db.func.sum(CareLog.cost), 0))
            .filter(CareLog.dog_id == self.id)
        )
        if start_date:
            query = query.filter(CareLog.date >= start_date)
        if end_date:
            query = query.filter(CareLog.date <= end_date)
        total = query.scalar() or 0
        return Decimal(str(total))


class CareLog(db.Model):
    __tablename__ = "care_logs"

    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(db.Integer, db.ForeignKey("dogs.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    type = db.Column(db.Enum(CareType), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    cost = db.Column(db.Numeric(10, 2), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    dog = db.relationship("Dog", back_populates="care_logs")
    user = db.relationship("User", back_populates="care_logs")


class Adopter(db.Model):
    """Adopter entity (BCNF: email is candidate key, determines name/phone)."""
    __tablename__ = "adopters"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    adoptions = db.relationship("Adoption", back_populates="adopter", lazy=True)


class Adoption(db.Model):
    __tablename__ = "adoptions"

    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(db.Integer, db.ForeignKey("dogs.id"), nullable=False, index=True)
    adopter_id = db.Column(db.Integer, db.ForeignKey("adopters.id"), nullable=False, index=True)
    application_date = db.Column(db.Date, nullable=False)
    decision_status = db.Column(db.Enum(DecisionStatus), nullable=False, default=DecisionStatus.PENDING, index=True)
    decision_date = db.Column(db.Date, nullable=True)
    adoption_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    dog = db.relationship("Dog", back_populates="adoptions")
    adopter = db.relationship("Adopter", back_populates="adoptions")
