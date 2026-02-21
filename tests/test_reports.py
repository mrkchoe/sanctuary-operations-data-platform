from datetime import date, timedelta

from app.extensions import db
from app.models import Adopter, Adoption, CareLog, CareType, Dog, DogStatus, DecisionStatus
from tests.conftest import login


def test_reports_requires_login(client):
    response = client.get("/reports/", follow_redirects=True)
    assert b"Sign in" in response.data or b"Login" in response.data


def test_reports_counts_and_sums(client, staff_user):
    login(client, email=staff_user.email)
    dog = Dog(
        name="Zara",
        estimated_age_years=2,
        sex="Female",
        breed="Cattle Dog",
        intake_date=date(2025, 1, 15),
        intake_source="Transfer",
        status=DogStatus.AVAILABLE,
    )
    db.session.add(dog)
    db.session.commit()

    care_log = CareLog(
        dog_id=dog.id,
        user_id=staff_user.id,
        date=date(2025, 1, 20),
        type=CareType.FEEDING,
        notes="High protein diet",
        cost=50.00,
    )
    db.session.add(care_log)

    adopter = Adopter(email="alex@example.com", name="Alex Doe", phone="555-1212")
    db.session.add(adopter)
    db.session.flush()
    adoption = Adoption(
        dog_id=dog.id,
        adopter_id=adopter.id,
        application_date=date(2025, 2, 1),
        decision_status=DecisionStatus.APPROVED,
        decision_date=date(2025, 2, 5),
        adoption_date=date(2025, 2, 10),
    )
    db.session.add(adoption)
    db.session.commit()

    response = client.get("/reports/")
    assert response.status_code == 200
    assert b"AVAILABLE" in response.data
    assert b"2025-01" in response.data
    assert b"2025-02" in response.data
    assert b"50.00" in response.data
