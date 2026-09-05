# Rule-Based Content Filter

A web application for creating rules that find and visually mark text. Matches can be highlighted with a selected color or displayed with a tooltip label.

## Tech stack

- Next.js and React
- FastAPI
- PostgreSQL
- SQLAlchemy and Alembic
- Docker Compose

## Run with Docker

You only need Git and Docker Desktop.

```bash
git clone https://github.com/arbiasi1/anchorzup-assignment.git
cd anchorzup-assignment
docker compose up --build
```

When the containers are ready, open:

- Application: <http://localhost:3000>
- API documentation: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/api/health>

Stop the application with:

```bash
docker compose down
```

The database data is kept when the containers stop. To also delete the database volume, use `docker compose down -v`.

## Features

- Create, view, edit, delete, enable, and disable rules
- `contains`, `startsWith`, and `exact` match types
- Highlight matches with a selected color
- Show custom tooltip labels
- Case-sensitive matching
- Rule priority
- Support for overlapping rules
- PostgreSQL rule persistence
- Responsive user interface

## Match types

| Type | Description |
|---|---|
| `contains` | Finds the keyword anywhere in the text |
| `startsWith` | Finds words that begin with the keyword |
| `exact` | Finds only a complete word or phrase |

Matching is case-insensitive unless **Case sensitive** is enabled.

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Check the API and database connection |
| `GET` | `/api/rules` | Retrieve all rules |
| `POST` | `/api/rules` | Create a rule |
| `PUT` | `/api/rules/{id}` | Update a rule |
| `DELETE` | `/api/rules/{id}` | Delete a rule |
| `POST` | `/api/process` | Process text with enabled rules |

## Run without Docker

Requirements: Python 3.11+, Node.js 20+, and PostgreSQL 14+.

Create a PostgreSQL database and user named `content_filter`, then copy `.env.example` to `.env`.

Start the backend:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

In another terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

## Tests

From the project root, run:

```bash
python -m pytest
```

Or, if the Docker containers are running:

```bash
docker compose exec backend python -m pytest
```

## Project structure

```text
app/         FastAPI backend and processing logic
frontend/    Next.js user interface
alembic/     Database migrations
tests/       Unit and API integration tests
```
