# goji/tests/test_auth.py

import pytest
import json
from app.user_management.models import User # Import User model for verification
from app.extensions import db as app_db # Import db for session access

# Define the base URL for auth API endpoints
BASE_URL = "/api/auth"

# --- Test Login ---

def test_login_success(client, db_session):
    print('FUNCTION CALL: test_login_success(client, db_session)')
    """Test successful login with valid credentials."""

    # Assuming 'admin' user with password 'testpassword' exists from conftest.py seeding
    payload = {"username": "testadmin", "password": "testpassword"}
    response = client.post(f"{BASE_URL}/login", json=payload)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["username"] == "testadmin"
    assert data["user"]["full_name"] == "Test Admin" # Assuming full_name is seeded

def test_login_invalid_password(client, db_session):
    """Test login with an invalid password."""
    payload = {"username": "admin", "password": "wrong_password"}
    response = client.post(f"{BASE_URL}/login", json=payload)
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "msg" in data
    assert "Bad username or password" in data["msg"]

def test_login_non_existent_user(client, db_session):
    """Test login with a username that does not exist."""
    payload = {"username": "non_existent_user", "password": "any_password"}
    response = client.post(f"{BASE_URL}/login", json=payload)
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "msg" in data
    assert "Bad username or password" in data["msg"]

def test_login_inactive_user(client, db_session):
    """Test login with a user account that is inactive."""
    # First, create an inactive user for testing
    inactive_user = User(username='inactiveuser', full_name='Inactive User', email='inactive@test.com', is_active=False)
    inactive_user.set_password('inactivepass')
    db_session.add(inactive_user)
    db_session.commit()

    payload = {"username": "inactiveuser", "password": "inactivepass"}
    response = client.post(f"{BASE_URL}/login", json=payload)
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "msg" in data
    assert "Bad username or password" in data["msg"] # Or a more specific message if implemented

def test_login_missing_fields(client, db_session):
    """Test login requests with missing fields."""
    # Missing password
    payload_missing_password = {"username": "admin"}
    response_missing_password = client.post(f"{BASE_URL}/login", json=payload_missing_password)
    # Flask might return 400 or 422 for missing JSON fields depending on setup
    assert response_missing_password.status_code == 400 
    
    # Missing username
    payload_missing_username = {"password": "testpassword"}
    response_missing_username = client.post(f"{BASE_URL}/login", json=payload_missing_username)
    assert response_missing_username.status_code == 400

    # Empty payload
    payload_empty = {}
    response_empty = client.post(f"{BASE_URL}/login", json=payload_empty)
    assert response_empty.status_code == 400

    # Payload is not JSON
    payload_not_json = "this is not json"
    response_no_json = client.post(f"{BASE_URL}/login", data=payload_not_json, content_type='application/json')
    assert response_no_json.status_code == 400


# --- Test Register ---

def test_register_success(client, db_session):
    """Test successful user registration."""
    payload = {
        "username": "testuser123",
        "password": "testpassword123",
        "email": "testuser123@example.com",
        "full_name": "Test User"
    }
    response = client.post(f"{BASE_URL}/register", json=payload)
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["username"] == "testuser123"
    assert data["email"] == "testuser123@example.com"
    assert "password_hash" not in data # Ensure password is not returned
    
    # Verify user was actually added to the database
    user = User.query.filter_by(username="testuser123").first()
    assert user is not None
    assert user.check_password("testpassword123")
    assert user.email == "testuser123@example.com"
    assert user.full_name == "Test User"

def test_register_username_exists(client, db_session):
    """Test registration attempt with an existing username."""
    # Assuming 'admin' user already exists from conftest.py seeding
    payload = {
        "username": "testadmin", # Existing username
        "password": "new_password",
        "email": "admin_new@example.com",
        "full_name": "Admin New"
    }
    response = client.post(f"{BASE_URL}/register", json=payload)
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert "msg" in data
    assert "Username already exists" in data["msg"]

def test_register_email_exists(client, db_session):
    """Test registration attempt with an existing email."""
    # Assuming 'admin' user already exists from conftest.py seeding
    payload = {
        "username": "another_user",
        "password": "another_password",
        "email": "admin@test.com", # Using admin's email
        "full_name": "Another User"
    }
    response = client.post(f"{BASE_URL}/register", json=payload)
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert "msg" in data
    assert "Email already exists" in data["msg"]

def test_register_password_too_short(client, db_session):
    """Test registration with a password shorter than the minimum length (6 characters)."""
    payload = {
        "username": "shortpassuser",
        "password": "short", # Password is too short
        "email": "shortpass@example.com",
        "full_name": "Short Pass User"
    }
    response = client.post(f"{BASE_URL}/register", json=payload)
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "password" in data # Check if the error is related to the password field
    # The exact error message might vary slightly based on Marshmallow version or custom validation
    assert "Field must be between 6 and 128 characters long." in data["password"][0] 

def test_register_invalid_email(client, db_session):
    """Test registration with an invalid email format."""
    payload = {
        "username": "invalidemailuser",
        "password": "validpassword",
        "email": "invalid-email-format", # Invalid email
        "full_name": "Invalid Email User"
    }
    response = client.post(f"{BASE_URL}/register", json=payload)
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "email" in data
    # The exact error message might vary slightly based on Marshmallow version or custom validation
    assert "Not a valid email address." in data["email"][0]

def test_register_missing_fields(client, db_session):
    """Test registration with missing required fields."""
    # Missing email
    payload_missing_email = {
        "username": "missingemail",
        "password": "validpassword",
        "full_name": "Missing Email"
    }
    response_missing_email = client.post(f"{BASE_URL}/register", json=payload_missing_email)
    # Flask might return 400 or 422 for missing JSON fields depending on setup
    assert response_missing_email.status_code == 400
    data_missing_email = json.loads(response_missing_email.data)
    assert "email" in data_missing_email
    assert "Missing data for required field." in data_missing_email["email"][0]

    # Missing password
    payload_missing_password = {
        "username": "missingpassword",
        "email": "missingpass@example.com",
        "full_name": "Missing Password"
    }
    response_missing_password = client.post(f"{BASE_URL}/register", json=payload_missing_password)
    assert response_missing_password.status_code == 400
    data_missing_password = json.loads(response_missing_password.data)
    assert "password" in data_missing_password
    assert "Missing data for required field." in data_missing_password["password"][0]