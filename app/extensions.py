# goji/app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from sqlalchemy import MetaData

# Define a naming convention for database constraints (indexes, foreign keys, etc.)
# This is a best practice to prevent migration errors with auto-generated names.
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create a metadata object with our naming convention
metadata = MetaData(naming_convention=convention)

# Instantiate SQLAlchemy with the custom metadata.
# The ModelBase class will handle the table name prefixing.
db = SQLAlchemy(metadata=metadata)

# Instantiate other extensions
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()
ma = Marshmallow()
