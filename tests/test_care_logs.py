from datetime import date

from app.extensions import db
from app.models import CareLog, CareType, Dog, DogStatus
from tests.conftest import login


def test_add_care_log_and_cost_total(client, staff_user):
    login(client, email=staff_user.email)
    dog = Dog(
        name="Rex",
        estimated_age_years=5,
        sex="Male",
        breed="Shepherd",
        intake_date=date.today(),
        intake_source="Stray",
        status=DogStatus.AVAILABLE,
    )
    db.session.add(dog)
    db.session.commit()

    response = client.post(
        f"/care/dogs/{dog.id}/new",
        data={
            "date": date.today().isoformat(),
            "type": CareType.VET_VISIT.value,
            "notes": "Vaccination",
            "cost": "125.50",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    log = CareLog.query.filter_by(dog_id=dog.id).first()
    assert log is not None

    detail = client.get(f"/dogs/{dog.id}")
    assert b"125.50" in detail.data
