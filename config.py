# goji/config.py
import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    # Turn off the Flask-SQLAlchemy event system and warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Use a secure, environment-variable-based secret key in production
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'a-very-secure-and-long-secret-key-that-you-must-change')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # Set a unique name for the migration version table for this project.
    MIGRATE_VERSION_TABLE = 'goji_alembic_version'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
    # Database connection details from environment variables with defaults
    DB_USER = os.environ.get('DB_USER', 'lining')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '111111')
    DB_HOST = os.environ.get('DB_HOST', 'server01.home.net')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'gojidb')
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# You can add other configurations like ProductionConfig or TestingConfig here
# class ProductionConfig(Config):
#     DEBUG = False
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
