import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.utils.db import Base
from app.main import app
from app.api import lot_routes, auth_routes, cv_routes
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.parking_spot import ParkingSpot
from app.models.parking_lot import ParkingLot
from app.models.spot_status import SpotStatus
from app.models.parking_analytics import ParkingAnalytics


# Seperate test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://parkvision:parkvision@db:5432/parkvision_test"
)

test_engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # ensure a clean schema for the test database
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

# Clean up database before each test
@pytest.fixture(autouse=True)
def clean_test_db():
    with test_engine.connect() as conn:
        conn.execute(text("SET session_replication_role = 'replica'"))
        
        conn.execute(text("DELETE FROM parking_analytics"))
        conn.execute(text("DELETE FROM spot_status"))
        conn.execute(text("DELETE FROM parking_spots"))
        conn.execute(text("DELETE FROM vehicles"))
        conn.execute(text("DELETE FROM parking_lots"))
        conn.execute(text("DELETE FROM users"))
        
        conn.execute(text("SET session_replication_role = 'origin'"))
        conn.commit()
    yield


@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()

# Override the get_db dependency to use test database
@pytest.fixture(scope="function")
def override_get_db():
    def _get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Apply override for all route modules that expose get_db
    app.dependency_overrides[lot_routes.get_db] = _get_db
    app.dependency_overrides[auth_routes.get_db] = _get_db
    app.dependency_overrides[cv_routes.get_db] = _get_db
    try:
        yield
    finally:
        app.dependency_overrides.clear()