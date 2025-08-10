# goji/app/models/__init__.py

# This file makes the 'models' directory a Python package.
# It's also a good place to import all your models so they can be
# easily discovered by Flask-Migrate.

from .base_model import ModelBase
from .organization_models import *
from .user_permission_models import *
# Import other model files as you create them
from .master_data_models import *
# from .process_models import *
# from .demand_models import *
