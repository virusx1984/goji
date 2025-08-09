# goji/app/models/base_model.py
import re
from ..extensions import db
from sqlalchemy.ext.declarative import declared_attr

# Define a dictionary to hardcode special pluralization rules.
# Key: Model class name in CamelCase.
# Value: Desired plural table name in snake_case (without the 'gj_' prefix).
SPECIAL_PLURALS = {
    'LegalEntity': 'legal_entities'
    # Add more exceptions here in the future as needed, for example:
    # 'Company': 'companies',
    # 'Person': 'people'
}

class ModelBase(db.Model):
    """
    An abstract base model that provides a default table name generation
    strategy. It converts the class name from CamelCase to a snake_case
    plural form and prefixes it with 'gj_'. It also handles special
    pluralization cases defined in the SPECIAL_PLURALS dictionary.
    """
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        """
        Dynamically calculates the table name based on the class name.
        """
        class_name = cls.__name__

        # Check if the current model class is defined in our special rules dictionary.
        if class_name in SPECIAL_PLURALS:
            # If it is, use the hardcoded value.
            plural_snake_case_name = SPECIAL_PLURALS[class_name]
        else:
            # If not, use the default rule: convert to snake_case and append 's'.
            snake_case_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
            plural_snake_case_name = f"{snake_case_name}s"
        
        return f"gj_{plural_snake_case_name}"