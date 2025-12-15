import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def use_test_db(override_get_db):
    pass

# Test data
test_user_data = {
    "username": "user",
    "email": "testuser@example.com",
    "password": "securepassword123"
}

test_login_data = {
    "username": "user",
    "password": "securepassword123"
}

# Test that user registration works
def test_register_user():
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert "id" in data
    assert "password" not in data

# Test that duplicate username/email registration is handled
def test_register_duplicate_username():
    client.post("/auth/register", json=test_user_data)
    
    duplicate_data = {
        "username": test_user_data["username"],
        "email": "different@example.com",
        "password": "password123"
    }
    response = client.post("/auth/register", json=duplicate_data)
    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]

# Test that duplicate email registration is handled
def test_register_duplicate_email():
    client.post("/auth/register", json=test_user_data)
    
    duplicate_data = {
        "username": "differentuser",
        "email": test_user_data["email"],
        "password": "password123"
    }
    response = client.post("/auth/register", json=duplicate_data)
    assert response.status_code == 400
    assert "Email already exists" in response.json()["detail"]

# Test that login works
def test_login_success():
    client.post("/auth/register", json=test_user_data)
    
    response = client.post("/auth/login", json=test_login_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert data["last_login"] is not None

# Test that login with wrong password fails
def test_login_invalid_password():
    client.post("/auth/register", json=test_user_data)
    
    wrong_login = {
        "username": test_user_data["username"],
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=wrong_login)
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

# Test that login for nonexistent user fails
def test_login_nonexistent_user():
    response = client.post("/auth/login", json=test_login_data)
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

# Test that getting user by ID works
def test_get_user():
    register_response = client.post("/auth/register", json=test_user_data)
    user_id = register_response.json()["id"]
    
    response = client.get(f"/auth/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == test_user_data["username"]

# Test that getting nonexistent user returns 404
def test_get_nonexistent_user():
    response = client.get("/auth/users/99999")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

# Test that getting all users works
def test_get_all_users():
    client.post("/auth/register", json=test_user_data)
    
    user_data_2 = {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_data_2)
    
    response = client.get("/auth/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

# Test that updating user works
def test_update_user():
    register_response = client.post("/auth/register", json=test_user_data)
    user_id = register_response.json()["id"]
    
    updates = {
        "username": "updateduser",
        "email": "updated@example.com"
    }
    response = client.put(f"/auth/users/{user_id}", json=updates)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateduser"
    assert data["email"] == "updated@example.com"

# Test that updating user password works
def test_update_user_password():
    register_response = client.post("/auth/register", json=test_user_data)
    user_id = register_response.json()["id"]
    
    updates = {"password": "newpassword123"}
    response = client.put(f"/auth/users/{user_id}", json=updates)
    assert response.status_code == 200
    
    login_data = {
        "username": test_user_data["username"],
        "password": "newpassword123"
    }
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

# Test that deleting a user works
def test_delete_user():
    register_response = client.post("/auth/register", json=test_user_data)
    user_id = register_response.json()["id"]
    
    response = client.delete(f"/auth/users/{user_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/auth/users/{user_id}")
    assert get_response.status_code == 404
