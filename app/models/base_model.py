# goji/app/models/base_model.py
import re
from ..extensions import db
from sqlalchemy.ext.declarative import declared_attr

class ModelBase(db.Model):
    """
    A base model class that automatically sets the table name
    with a 'gj_' prefix and converts the class name from CamelCase
    to snake_case plural form.
    e.g., BusinessUnit -> gj_business_units
    """
    __abstract__ = True  # This ensures that SQLAlchemy does not create a table for ModelBase itself.

    @declared_attr
    def __tablename__(cls):
        # Converts CamelCase class name to snake_case
        snake_case_name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        # Appends 's' to make it plural and adds the prefix
        return f"gj_{snake_case_name}s"
