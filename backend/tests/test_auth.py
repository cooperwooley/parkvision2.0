import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db import Base, engine, SessionLocal
from app.services.auth_service import hash_password, verify_password, add_user, authenticate_user

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test that hash_password changes password
def test_hash_password():
    password = "test_password_123"
    hashed = hash_password(password)
    
    assert hashed != password
    
    assert isinstance(hashed, str)

# Test verify_password function
def test_verify_password_correct():
    password = "correct_password"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True

# Test verify_password with incorrect password
def test_verify_password_incorrect():
    password = "correct_password"
    wrong_password = "wrong_password"
    hashed = hash_password(password)
    
    assert verify_password(wrong_password, hashed) is False

# Test that add_user correctly adds a user and hashes the password
def test_add_user(db_session):
    username = "testuser"
    email = "test@example.com"
    password = "secure_password_123"
    
    user = add_user(db_session, username, email, password)
    
    assert user.username == username
    assert user.email == email
    
    assert user.password_hash != password
    
    assert verify_password(password, user.password_hash) is True

# Test that add_user hashes passwords uniquely
def test_add_user_hashes_correctly(db_session):
    password1 = "password_one"
    password2 = "password_two"
    
    user1 = add_user(db_session, "user1", "user1@example.com", password1)
    user2 = add_user(db_session, "user2", "user2@example.com", password2)
    
    assert user1.password_hash != user2.password_hash
    
    assert verify_password(password1, user1.password_hash) is True
    assert verify_password(password2, user2.password_hash) is True
    
    assert verify_password(password2, user1.password_hash) is False
    assert verify_password(password1, user2.password_hash) is False

# Test that authenticate_user works correctly
def test_authenticate_user_success(db_session):
    username = "testuser"
    email = "test@example.com"
    password = "correct_password"
    
    add_user(db_session, username, email, password)
    
    authenticated_user = authenticate_user(db_session, username, password)
    assert authenticated_user is not None
    assert authenticated_user.username == username
    assert authenticated_user.email == email

# Test that authenticate_user fails with wrong password
def test_authenticate_user_wrong_password(db_session):
    username = "testuser"
    email = "test@example.com"
    password = "correct_password"
    
    add_user(db_session, username, email, password)
    
    authenticated_user = authenticate_user(db_session, username, "wrong_password")
    assert authenticated_user is None

# Test that authenticate_user works correctly for nonexistent user
def test_authenticate_user_nonexistent(db_session):
    authenticated_user = authenticate_user(db_session, "nonexistent", "any_password")
    assert authenticated_user is None
