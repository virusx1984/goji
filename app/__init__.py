# goji/app/__init__.py
from flask import Flask
from config import DevelopmentConfig

from .extensions import db, migrate, bcrypt, jwt, cors, ma

def create_app(config_class=DevelopmentConfig):
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    ma.init_app(app)

    # --- CHANGE: Import blueprints directly from the 'routes.py' file of each module ---
    from .apis.auth import bp as auth_bp
    from .master_data.routes import bp as master_data_bp
    from .user_management.routes import bp as user_management_bp
    from .organization.routes import bp as organization_bp
    from .process.routes import bp as process_bp
    from .demand.routes import bp as demand_bp

    
    # Register all blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(master_data_bp)
    app.register_blueprint(user_management_bp)
    app.register_blueprint(organization_bp)
    app.register_blueprint(process_bp)
    app.register_blueprint(demand_bp)
    

    # Import and register custom CLI commands
    from .commands import seed_data_command
    app.cli.add_command(seed_data_command, "seed")

    return app
