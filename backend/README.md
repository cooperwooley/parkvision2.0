# ParkVision Backend

A FastAPI-based parking management system backend with Docker support.

## Prerequisites

- Docker and Docker Compose installed on your system
- Or Python 3.11+ with pip (for local development)

## Quick Start

### Running with Docker (Recommended)

**Start the backend:**
```bash
docker compose up
```

This will:
- Build the backend image
- Start a PostgreSQL database container
- Start the backend API server on `http://localhost:8000`

The database will be initialized automatically. The API will be available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

**Stop the backend:**
```bash
docker compose down
```

**Clean up (reset database and remove volumes):**
```bash
docker compose down -v
```

---

## Running Tests

### Tests in Docker

**Run all tests:**
```bash
docker compose exec backend pytest
```

**Run specific test file:**
```bash
# tests live under `app/tests` in the container; example paths below
docker compose exec backend pytest app/tests/test_parking_lot.py -v
docker compose exec backend pytest app/tests/test_auth_routes.py -v
```

Note: Tests run inside the container use a separate test database by default. The test database URL is read from the `TEST_DATABASE_URL` environment variable (defaults to `postgresql://parkvision:parkvision@db:5432/parkvision_test`). The test fixtures in `app/tests/conftest.py` create/drop tables and clean data so your production `parkvision` database is not modified when running tests.

**Run tests with coverage:**
```bash
docker compose exec backend pytest --cov=app tests/
```

### Tests Locally (requires local setup)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run tests:**
```bash
pytest
```

**Run specific test file:**
**Run specific test file:**
```bash
pytest app/tests/test_auth_routes.py -v
pytest app/tests/test_parking_lot.py -v
```

---

## Local Development (without Docker)

### Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** (or update existing one):
   ```env
   DATABASE_URL=postgresql://parkvision:parkvision@localhost:5432/parkvision
   ```

5. **Run PostgreSQL locally** (you'll need to set up PostgreSQL separately)

### Run the server locally:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000` with hot-reload enabled.

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── api/
│   │   ├── auth_routes.py      # Authentication endpoints
│   │   ├── lot_routes.py       # Parking lot endpoints
│   │   └── analytics_routes.py # Analytics endpoints
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── vehicle.py
│   │   ├── parking_lot.py
│   │   ├── parking_spot.py
│   │   ├── spot_status.py
│   │   └── parking_analytics.py
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   │   ├── auth_service.py     # Password hashing & authentication
│   │   ├── cv_integration.py   # CV system integration
│   │   └── analytics_service.py
│   └── utils/
│       ├── db.py               # Database setup
│       └── config.py           # Configuration
├── app/
│   └── tests/                  # Pytest test files and fixtures (run inside container)
│       ├── conftest.py         # Pytest configuration and test DB fixtures
│       ├── test_auth_routes.py # Authentication route tests
│       └── test_parking_lot.py # Parking lot route tests
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
```

---

## API Endpoints

### Parking Lots
- `GET /lots/` - Get all parking lots
- `POST /lots/` - Create a new parking lot
- `GET /lots/{lot_id}` - Get a specific parking lot
- `PUT /lots/{lot_id}` - Update a parking lot
- `DELETE /lots/{lot_id}` - Delete a parking lot

### Authentication
- `POST /auth/signup` - Create a new user with password hashing
- `POST /auth/login` - Authenticate a user
Note: the implementation exposes `/auth/register` for creating users (not `/auth/signup`).
So the correct endpoints are:
- `POST /auth/register` - Create a new user with password hashing
- `POST /auth/login` - Authenticate a user

### Analytics
- Various endpoints for parking analytics and statistics

---

## Authentication

The backend includes secure authentication with password hashing using bcrypt:

- Passwords are hashed using bcrypt before storage
- User signup validates and securely stores passwords
- Authentication verifies password hashes at login
- See `app/services/auth_service.py` for implementation details

---

## Database

### PostgreSQL in Docker

The `docker-compose.yml` includes a PostgreSQL service that:
- Uses credentials: `user=parkvision`, `password=parkvision`
- Creates database: `parkvision`
- Exposes port `5432`
- Stores data in a named volume `postgres_data`

### Database Access

**Connect to the database from inside Docker:**
```bash
docker compose exec db psql -U parkvision -d parkvision
```

---

## Troubleshooting

### Docker Issues

**Port already in use:**
```bash
# Change ports in docker-compose.yml or stop conflicting services
docker ps
docker stop <container_id>
```

**Database connection errors:**
```bash
# Ensure database is healthy
docker compose up -d
docker compose ps  # Check status
```

**Container won't start:**
```bash
# View logs
docker compose logs backend
docker compose logs db
```

### Reset Everything

```bash
# Stop containers and remove volumes
docker compose down -v

# Remove cached images
docker rmi parkvision_backend

# Start fresh
docker compose up
```

---

## Development Tips

### Hot Reload

The backend runs with `--reload` flag, so changes to Python files are automatically reloaded.

### Database Migrations

If you add new models, create the tables:
```bash
# Inside container
docker compose exec backend python -c "from app.utils.db import Base, engine; from app.models import *; Base.metadata.create_all(bind=engine)"
```

### Running Tests During Development

```bash
# Watch mode with pytest (requires pytest-watch)
ptw  # or: docker compose exec backend ptw
```

---

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://parkvision:parkvision@db:5432/parkvision

# API
DEBUG=True
LOG_LEVEL=info
```

---

## Dependencies

Key dependencies are listed in `requirements.txt`:
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM for database
- **psycopg2** - PostgreSQL adapter
- **bcrypt** - Password hashing
- **pytest** - Testing framework
- **httpx** - HTTP client for testing
- **python-dotenv** - Environment variable management

---

## Contributing

1. Create a new branch for your feature
2. Make your changes and test locally
3. Run tests to ensure nothing breaks
4. Submit a pull request

---
