# goji/run.py
import os
from app import create_app

# Load the configuration from an environment variable or default to development
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
