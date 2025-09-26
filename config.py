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
    MIGRATE_VERSION_TABLE = 'gj_alembic_version'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
    # Database connection details from environment variables with defaults
    #region --- PostgreSQL---
    # DB_USER = os.environ.get('DB_USER', 'lining')
    # DB_PASSWORD = os.environ.get('DB_PASSWORD', '111111')
    # DB_HOST = os.environ.get('DB_HOST', 'server01.home.net')
    # DB_PORT = os.environ.get('DB_PORT', '5432')
    # DB_NAME = os.environ.get('DB_NAME', 'gojidb')
    
    # SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    #endregion === PostgreSQL ===

    #region --- Oracle 11g Test ---
    DB_USER = os.environ.get('DB_USER', 'hdibks')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'hdibks*168')
    DB_HOST = os.environ.get('DB_HOST', 'server01.home.net')
    DB_PORT = os.environ.get('DB_PORT', '1521')
    DB_NAME = os.environ.get('DB_NAME', 'xe')
    SQLALCHEMY_DATABASE_URI = f'oracle+oracledb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    #endregion === Oracle 11g ===

    #region --- Oracle 11g ---
    # DB_USER = os.environ.get('DB_USER', 'hdibks')
    # DB_PASSWORD = os.environ.get('DB_PASSWORD', 'hdibks*168')
    # DB_HOST = os.environ.get('DB_HOST', 'szdb74.eavarytech.com')
    # DB_PORT = os.environ.get('DB_PORT', '1521')
    # DB_NAME = os.environ.get('DB_NAME', 'ictdb1')
    # SQLALCHEMY_DATABASE_URI = f'oracle+cx_oracle://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    #endregion === Oracle 11g ===

# You can add other configurations like ProductionConfig or TestingConfig here
# class ProductionConfig(Config):
#     DEBUG = False
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
