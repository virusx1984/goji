# goji/app/__init__.py
from flask import Flask
from config import DevelopmentConfig # Import configurations

# Import extensions
from .extensions import db, migrate, bcrypt, jwt, cors, ma

def create_app(config_class=DevelopmentConfig):
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)
    
    # Load configuration from the config object
    app.config.from_object(config_class)

    # Initialize extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    ma.init_app(app)

    # --- Blueprints from the old 'apis' structure that are not yet refactored ---
    from .apis.auth import bp as auth_bp
    from .master_data import bp as customers_bp
    
    from .user_management import bp as user_management_bp
    from .organization import bp as organization_bp
    
    # Register all blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(user_management_bp)
    app.register_blueprint(organization_bp)

    # Import and register custom CLI commands
    from .commands import seed_data_command
    app.cli.add_command(seed_data_command, "seed")

    return app
