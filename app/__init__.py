# goji/app/__init__.py

import oracledb
import sys

# --- Place this at the top of your application's entry point ---
# Initialize the Oracle Client to enable "Thick Mode".
# Since your Instant Client is already in the system PATH, the lib_dir parameter is usually not needed.
try:
    oracledb.init_oracle_client()
except Exception as e:
    print("Error initializing Oracle Client:", e)



from flask import Flask
import config
from .extensions import db, migrate, bcrypt, jwt, cors, ma
from .commands import seed_data_command, empty_db_command

# A dictionary to map configuration names (strings) to their corresponding classes.
# This allows the factory to be called with a string name like 'development'.
config_by_name = {
    'development': config.DevelopmentConfig,
    'testing': config.TestingConfig,
    # 'production': config.ProductionConfig, # Uncomment when you create a ProductionConfig
}

def create_app(config_name='development'):
    """
    Application factory function to create and configure the Flask app.
    This function is the main entry point for creating the application instance.

    Args:
        config_name (str): The name of the configuration to use (e.g., 'development').
    """
    app = Flask(__name__)

    # --- Step 1: Load Configuration ---
    # Look up the configuration class from the dictionary and load it.
    # This is the most critical step to ensure all settings, including
    # MIGRATE_VERSION_TABLE, are loaded before extensions are initialized.
    config_object = config_by_name.get(config_name, config.DevelopmentConfig)
    app.config.from_object(config_object)


    # --- Step 2: Initialize Extensions ---
    # Pass the fully configured app object to each extension's init_app method.
    # db.init_app(app)
    # migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    ma.init_app(app)

    # --- Step 3: Register Blueprints ---
    # Import blueprints inside the factory to prevent circular import issues.
    from .apis.auth import bp as auth_bp
    from .user_management.routes import bp as user_management_bp
    from .organization.routes import bp as organization_bp
    from .master_data.routes import bp as master_data_bp
    from .process.routes import bp as process_bp
    from .demand.routes import bp as demand_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_management_bp)
    app.register_blueprint(organization_bp)
    app.register_blueprint(master_data_bp)
    app.register_blueprint(process_bp)
    app.register_blueprint(demand_bp)

    # --- Step 4: Register Custom CLI Commands ---
    app.cli.add_command(seed_data_command)
    app.cli.add_command(empty_db_command)

    return app