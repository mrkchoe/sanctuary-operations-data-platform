# sanctuary-operations-data-platform

Full-stack data platform and web application modeling the operational workflows of an animal sanctuary. The system supports dog intake tracking, care logs, adoption workflows, and SQL-based reporting dashboards backed by a normalized relational schema and secure access controls.

This project demonstrates how operational data can be structured, validated, and surfaced for organizational decision-making.

---

## Architecture

Flask web application → relational database → SQL reporting dashboards

Core components:

- Flask backend for operational workflows and secure access  
- Normalized relational schema for sanctuary data management  
- Alembic migrations for schema versioning  
- SQL queries and dashboards for operational reporting  
- Authentication and role-based access control for secure data access  

---

## Features

- Secure authentication with hashed passwords and CSRF-protected forms  
- Role-based access control (admin vs staff)  
- Dog intake management, edits, and soft-archiving  
- Care logs with optional costs and per-dog cost rollups  
- Adoption applications with approval workflow  
- Reporting dashboards for status counts, monthly trends, and top cost drivers  

---

## Data Model Overview

The schema is designed in **Boyce–Codd normal form (BCNF)** so that every determinant is a candidate key.

Adopter details are stored in a separate `adopters` table keyed by email to avoid redundancy and ensure consistent references from adoption records.

### Core Tables

**users**  
id, email (unique), password_hash, role, created_at

**dogs**  
id, name, estimated_age_years, sex, breed, intake_date, intake_source, status, archived_at, created_at

**care_logs**  
id, dog_id, user_id, date, type, notes, cost, created_at

**adopters**  
id, email (unique), name, phone, created_at

**adoptions**  
id, dog_id, adopter_id, application_date, decision_status, decision_date, adoption_date, notes, created_at

### Indexing

Indexes are applied to improve query performance:

- dogs.status  
- dogs.intake_date  
- care_logs.dog_id  
- care_logs.date  
- adoptions.dog_id  
- adoptions.decision_status  
- adopters.email  

---

## Local Setup

Create a Python environment and install dependencies:

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env   # Windows: copy .env.example .env
```

Defaults are configured for local development using SQLite.

---

## Database and Migrations

Apply database migrations:

```bash
alembic upgrade head
```

Tables will also be created automatically on first application run if migrations have not been applied.

---

## Run the Application

```bash
python run.py
```

The application will start a local development server.

---

## Example Login and Demo Data

On first run with an empty database, the app creates:

- a demo account  
- sample dogs  
- example care logs  
- adoption records  

| Email | Password |
| staff@example.com | demo1234 |

Use the account to explore:

- Dog intake and status management  
- Care log tracking  
- Adoption workflow  
- Reporting dashboards  

---

## Run Tests

```bash
pytest
```

---

## Configuration Notes

- SQLite is used by default for local development (`sqlite:///sanctuary.db`)  
- To use Postgres, set `DATABASE_URL` to your connection string  
- `SECRET_KEY` must be set in production  

---

## Security Notes

- Passwords are stored using Werkzeug password hashing  
- All forms use CSRF protection via Flask-WTF  
- Role-based access control restricts sensitive operations  
- Care logs record the user responsible for each entry for auditing purposes  

---

## Concepts Demonstrated

- Relational schema design in **BCNF**  
- Operational data modeling  
- Role-based access control (RBAC)  
- Secure authentication workflows  
- Database migrations with Alembic  
- SQL reporting for operational analytics  

---

## Disclaimer

This is a hypothetical demo project created for portfolio purposes. No real data is included.
