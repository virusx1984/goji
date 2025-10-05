# goji/tests/conftest.py

import pytest
import os
from flask import Flask
from app import create_app  # Assuming your app factory is in goji/app/__init__.py
from app.extensions import db as app_db # Import db from extensions
from app.user_management.models import User, Role, Permission # Import models for seeding

# --- Configuration for Testing ---
# It's good practice to have a dedicated testing configuration.
# If you don't have one, you can define it here or in config.py.
# For this example, we'll assume a 'testing' config exists or we'll override settings.

@pytest.fixture(scope='session')
def app():
    """
    Provides a session-wide test application instance.
    Uses an in-memory SQLite database for testing.
    """
    # Create the app using the factory function
    app = create_app('testing') # Or 'development' if you don't have a specific testing config

    # The following overrides are good, but if 'testing' config is set correctly,
    # they might be redundant or could be removed if TestingConfig handles them.
    # However, keeping them ensures the in-memory SQLite is definitely used.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'a-test-secret-key-that-is-not-secure' # Use a test key

    # Ensure the app context is pushed for database operations
    with app.app_context():
        # Create all database tables
        app_db.create_all()

        # --- Seed Test Data ---
        # It's crucial to have predictable data for tests.
        # You might want to create a dedicated test_seed function or
        # seed specific data here rather than relying on the full 'flask seed' command.

        # Example: Seed a test user
        try:
            # Check if user already exists to avoid errors on repeated runs (e.g., during development)
            if not User.query.filter_by(username='testadmin').first():
                admin_user = User(username='testadmin', full_name='Test Admin', email='admin@test.com')
                admin_user.set_password('testpassword')
                app_db.session.add(admin_user)
                
                # Add other necessary test data like roles, permissions if needed for tests
                # For example, if you need to test role-based access:
                # admin_role = Role(name='TestAdminRole')
                # admin_permission = Permission(name='test:permission')
                # admin_user.roles.append(admin_role)
                # admin_role.permissions.append(admin_permission)
                
                app_db.session.commit()
        except Exception as e:
            app_db.session.rollback()
            pytest.fail(f"Failed to seed test data: {e}")

        yield app  # Provide the app instance to the tests

        # --- Clean up ---
        # Drop all tables after the test session is complete
        app_db.drop_all()

@pytest.fixture(scope='session')
def client(app):
    """
    Provides a session-wide test client for making requests to the Flask app.
    """
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """
    Provides a transactional scope around each test function.
    Ensures that each test runs with a clean database state and rolls back changes.
    """
    connection = app_db.engine.connect()
    transaction = connection.begin()
    session = app_db.session(bind=connection)
    
    # Yield the session to the test function
    yield session
    
    # Rollback the transaction after the test function completes
    transaction.rollback()
    # Close the session and connection
    session.close()
    connection.close()

# You can add more fixtures here if needed, for example:
# @pytest.fixture(scope='session')
# def logged_in_client(client, db_session):
#     """Fixture to get a client that is already logged in."""
#     login_payload = {"username": "testadmin", "password": "testpassword"}
#     login_response = client.post("/api/auth/login", json=login_payload)
#     token = json.loads(login_response.data)["access_token"]
#     
#     # Store the token for subsequent requests
#     client.token = token
#     
#     yield client