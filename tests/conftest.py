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
    print('FUNCTION CALL: app() session')
    """
    Provides a session-wide test application instance.
    Uses an in-memory SQLite database for testing.
    """
    # 1. Create the app instance.
    #    This will load TestingConfig because we pass 'testing'.
    app = create_app('testing') 

    # 2. Override configuration for testing (ensures SQLite is used).
    #    These are crucial if create_app('testing') doesn't perfectly isolate config.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'a-test-secret-key-that-is-not-secure'

    # Ensure the app context is pushed for database operations
    with app.app_context():
        # --- CRUCIAL STEP: Initialize SQLAlchemy extension here ---
        # Since db.init_app(app) was commented out in create_app,
        # we initialize it here within the app context.
        # This ensures it uses the app's current configuration (which is for testing/SQLite).
        app_db.init_app(app) 
        
        # Now create all tables using the correctly configured SQLite engine
        app_db.create_all()

        # --- Seed Test Data ---
        try:
            if not User.query.filter_by(username='testadmin').first():
                admin_user = User(username='testadmin', full_name='Test Admin', email='admin@test.com')
                admin_user.set_password('testpassword')
                app_db.session.add(admin_user)
                app_db.session.commit()
        except Exception as e:
            app_db.session.rollback()
            pytest.fail(f"Failed to seed test data: {e}")

        yield app  # Provide the app instance to the tests

        # --- Clean up ---
        app_db.drop_all()
        # Flask-SQLAlchemy usually handles engine disposal on app context teardown.
        # If you encounter issues, you might need to explicitly dispose:
        # if app_db.engine:
        #     app_db.engine.dispose()

@pytest.fixture(scope='session')
def client(app):
    print('FUNCTION CALL: client(app) session')
    """
    Provides a session-wide test client for making requests to the Flask app.
    """
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    print('FUNCTION CALL: db_session(app) function')
    """
    Provides a transactional scope around each test function.
    Ensures that each test runs with a clean database state and rolls back changes.
    """
    with app.app_context(): # Ensure context is active for session operations
        connection = app_db.engine.connect()
        transaction = connection.begin()
        session = app_db.session(bind=connection)
        
        yield session
        
        transaction.rollback()
        session.close()
        connection.close()