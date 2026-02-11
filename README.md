# sanctuary-operations-data-platform

A full-stack Flask portfolio app for a hypothetical dog sanctuary. It supports authentication, dog intake and care tracking, adoption workflows, and SQL-based reporting dashboards with a clean data model and secure access controls.

## Features
- Secure authentication with hashed passwords and CSRF-protected forms
- Role-based access control (admin vs staff)
- Dog intake management, edits, and soft-archiving
- Care logs with optional costs and per-dog cost rollups
- Adoption applications with approval workflow
- Reporting dashboards for status counts, monthly trends, and top cost drivers

## Data model overview
- `users`: id, email (unique), password_hash, role, created_at
- `dogs`: id, name, estimated_age_years, sex, breed, intake_date, intake_source, status, archived_at, created_at
- `care_logs`: id, dog_id, user_id, date, type, notes, cost, created_at
- `adoptions`: id, dog_id, adopter_name, adopter_email, adopter_phone, application_date, decision_status, decision_date, adoption_date, notes, created_at

Indexes are applied to `dogs.status`, `dogs.intake_date`, `care_logs.dog_id/date`, and `adoptions.dog_id/decision_status`.

## Local setup
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the environment template and set values:
```bash
cp .env.example .env
```

## Database and migrations
```bash
alembic upgrade head
```

## Run the app
```bash
python run.py
```

## Run tests
```bash
pytest
```

## Configuration notes
- SQLite is the default for local development (`sqlite:///sanctuary.db`).
- To use Postgres, set `DATABASE_URL` to your connection string.
- `SECRET_KEY` must be set in production.

## Security notes
- Passwords are stored using Werkzeug hashing.
- All forms use CSRF protection via Flask-WTF.
- RBAC enforces role permissions: staff can manage dogs/care/adoptions; admin is reserved for user-level operations.
- Care logs store the user who created each entry for auditing.

## Disclaimer

This is a hypothetical demo project for portfolio use only. No real data is included.
