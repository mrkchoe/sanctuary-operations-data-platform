from datetime import date

from app.extensions import db
from app.models import Dog, DogStatus
from tests.conftest import login


def test_create_and_edit_dog(client, staff_user):
    login(client, email=staff_user.email)

    response = client.post(
        "/dogs/new",
        data={
            "name": "Buddy",
            "estimated_age_years": "3",
            "sex": "Male",
            "breed": "Labrador",
            "intake_date": date.today().isoformat(),
            "intake_source": "Shelter transfer",
            "status": DogStatus.INTAKE.value,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    dog = Dog.query.filter_by(name="Buddy").first()
    assert dog is not None

    response = client.post(
        f"/dogs/{dog.id}/edit",
        data={
            "name": "Buddy",
            "estimated_age_years": "4",
            "sex": "Male",
            "breed": "Labrador",
            "intake_date": date.today().isoformat(),
            "intake_source": "Shelter transfer",
            "status": DogStatus.AVAILABLE.value,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    updated = db.session.get(Dog, dog.id)
    assert updated.estimated_age_years == 4.0
    assert updated.status == DogStatus.AVAILABLE


def test_archive_hides_from_list(client, staff_user):
    login(client, email=staff_user.email)
    dog = Dog(
        name="Molly",
        estimated_age_years=2,
        sex="Female",
        breed="Husky",
        intake_date=date.today(),
        intake_source="Owner surrender",
        status=DogStatus.AVAILABLE,
    )
    db.session.add(dog)
    db.session.commit()

    response = client.get("/dogs/")
    assert b"Molly" in response.data

    client.post(f"/dogs/{dog.id}/archive", follow_redirects=True)
    response = client.get("/dogs/")
    assert b"Molly" not in response.data
