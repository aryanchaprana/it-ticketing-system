"""
Centralized Flask extension instances.
Initialized here to avoid circular imports.
Bound to the app in the factory function inside app/__init__.py.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to continue.'
login_manager.login_message_category = 'warning'

migrate = Migrate()
csrf = CSRFProtect()
