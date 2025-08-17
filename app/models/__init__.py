# goji/app/models/__init__.py

# This file makes the 'models' directory a Python package.
# It's also a good place to import all your models so they can be
# easily discovered by Flask-Migrate.

from .base_model import ModelBase
from ..organization.models import *
from ..user_management.models import *
from ..master_data.models import *

