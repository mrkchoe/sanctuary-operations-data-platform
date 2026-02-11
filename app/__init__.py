from flask import Flask, redirect, url_for
from flask_login import login_required

from app.config import Config
from app.extensions import csrf, db, login_manager


def _ensure_tables_and_demo_user(app: Flask) -> None:
    """Create tables from models if missing; seed demo user and example data when empty."""
    from datetime import date

    with app.app_context():
        db.create_all()
        from app.models import (
            Adoption,
            CareLog,
            CareType,
            DecisionStatus,
            Dog,
            DogStatus,
            User,
            UserRole,
        )

        if User.query.count() == 0:
            demo = User(email="staff@example.com", role=UserRole.STAFF)
            demo.set_password("demo1234")
            db.session.add(demo)
            db.session.commit()

        if Dog.query.count() == 0:
            demo_user = User.query.filter_by(email="staff@example.com").first()
            today = date.today()
            y, m = today.year, today.month

            dogs = [
                Dog(
                    name="Buddy",
                    estimated_age_years=3.0,
                    sex="M",
                    breed="Labrador Retriever",
                    intake_date=date(y, m, 1),
                    intake_source="Owner surrender",
                    status=DogStatus.AVAILABLE,
                ),
                Dog(
                    name="Luna",
                    estimated_age_years=1.5,
                    sex="F",
                    breed="German Shepherd",
                    intake_date=date(y, m, 5),
                    intake_source="Stray",
                    status=DogStatus.INTAKE,
                ),
                Dog(
                    name="Max",
                    estimated_age_years=5.0,
                    sex="M",
                    breed="Golden Retriever",
                    intake_date=date(y, m, 10),
                    intake_source="Rescue transfer",
                    status=DogStatus.MEDICAL_HOLD,
                ),
                Dog(
                    name="Daisy",
                    estimated_age_years=2.0,
                    sex="F",
                    breed="Beagle",
                    intake_date=date(y, m, 15),
                    intake_source="Owner surrender",
                    status=DogStatus.ADOPTED,
                ),
                Dog(
                    name="Rocky",
                    estimated_age_years=4.0,
                    sex="M",
                    breed="Mixed",
                    intake_date=date(y, m, 20),
                    intake_source="Stray",
                    status=DogStatus.FOSTER,
                ),
            ]
            for d in dogs:
                db.session.add(d)
            db.session.commit()

            if demo_user:
                buddy_id = Dog.query.filter_by(name="Buddy").first().id
                luna_id = Dog.query.filter_by(name="Luna").first().id
                max_id = Dog.query.filter_by(name="Max").first().id
                daisy_id = Dog.query.filter_by(name="Daisy").first().id
                care_logs = [
                    CareLog(dog_id=buddy_id, user_id=demo_user.id, date=today, type=CareType.WALK, notes="Morning walk", cost=None),
                    CareLog(dog_id=buddy_id, user_id=demo_user.id, date=today, type=CareType.FEEDING, notes="Breakfast", cost=None),
                    CareLog(dog_id=luna_id, user_id=demo_user.id, date=today, type=CareType.VET_VISIT, notes="Checkup", cost=85.00),
                    CareLog(dog_id=max_id, user_id=demo_user.id, date=today, type=CareType.MEDS, notes="Flea treatment", cost=25.50),
                ]
                for cl in care_logs:
                    db.session.add(cl)
                db.session.add(
                    Adoption(
                        dog_id=daisy_id,
                        adopter_name="Jane Smith",
                        adopter_email="jane@example.com",
                        adopter_phone="555-0100",
                        application_date=date(y, m, 18),
                        decision_status=DecisionStatus.APPROVED,
                        decision_date=date(y, m, 19),
                        adoption_date=date(y, m, 20),
                        notes="Great match.",
                    )
                )
                db.session.add(
                    Adoption(
                        dog_id=luna_id,
                        adopter_name="John Doe",
                        adopter_email="john@example.com",
                        application_date=today,
                        decision_status=DecisionStatus.PENDING,
                        notes="Awaiting home check.",
                    )
                )
            db.session.commit()


def create_app(config_object: type[Config] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_object or Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.auth.routes import auth_bp
    from app.dogs.routes import dogs_bp
    from app.care.routes import care_bp
    from app.adoptions.routes import adoptions_bp
    from app.reports.routes import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dogs_bp)
    app.register_blueprint(care_bp)
    app.register_blueprint(adoptions_bp)
    app.register_blueprint(reports_bp)

    _ensure_tables_and_demo_user(app)

    @app.route("/")
    @login_required
    def index():
        return redirect(url_for("dogs.list_dogs"))

    return app
