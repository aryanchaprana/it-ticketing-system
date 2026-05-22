"""
Flask Application Factory for Nash Energy IT Ticketing System.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask

from config import config
from app.extensions import db, login_manager, migrate, csrf


def create_app(config_name: str = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config[config_name])

    _ensure_upload_directory(app)
    _init_extensions(app)
    _register_blueprints(app)
    _configure_login_manager(app)
    _register_template_utilities(app)
    _register_error_handlers(app)
    _configure_logging(app)

    with app.app_context():
        db.create_all()
        _seed_admin_user(app)

    app.logger.info(f'Nash Energy IT Ticketing — startup complete [env={config_name}]')
    return app


def _ensure_upload_directory(app):
    upload_folder = app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
    os.makedirs(upload_folder, exist_ok=True)


def _init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)


def _register_blueprints(app):
    from app.public.routes   import public_bp
    from app.auth.routes     import auth_bp
    from app.admin.routes    import admin_bp
    from app.staff.routes    import staff_bp
    from app.employee.routes import employee_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp,     url_prefix='/auth')
    app.register_blueprint(admin_bp,    url_prefix='/admin')
    app.register_blueprint(staff_bp,    url_prefix='/staff')
    app.register_blueprint(employee_bp, url_prefix='/employee')


def _configure_login_manager(app):
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        user = db.session.get(User, int(user_id))
        if user and user.is_active:
            return user
        return None


def _register_template_utilities(app):
    from datetime import datetime, timezone
    from app.models import TicketStatus, TicketPriority, UserRole, TicketCategory

    @app.context_processor
    def inject_globals():
        return {
            'now':            datetime.now(timezone.utc),
            'TicketStatus':   TicketStatus,
            'TicketPriority': TicketPriority,
            'UserRole':       UserRole,
            'TicketCategory': TicketCategory,
        }

    @app.template_filter('datetimeformat')
    def datetimeformat(value, fmt='%d %b %Y, %H:%M'):
        if value is None:
            return 'N/A'
        if hasattr(value, 'strftime'):
            return value.strftime(fmt)
        return value

    @app.template_filter('priority_badge')
    def priority_badge(priority_value: str) -> str:
        mapping = {
            'High':   'bg-danger',
            'Medium': 'bg-warning text-dark',
            'Low':    'bg-success',
        }
        return mapping.get(priority_value, 'bg-secondary')

    @app.template_filter('status_badge')
    def status_badge(status_value: str) -> str:
        mapping = {
            'Open':        'bg-primary',
            'Assigned':    'bg-info text-dark',
            'In Progress': 'bg-warning text-dark',
            'Solved':      'bg-success',
            'Closed':      'bg-secondary',
        }
        return mapping.get(status_value, 'bg-secondary')


def _register_error_handlers(app):
    from flask import render_template

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def file_too_large(e):
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f'Server Error: {e}')
        return render_template('errors/500.html'), 500


def _configure_logging(app):
    if not app.debug:
        os.makedirs('logs', exist_ok=True)
        file_handler = RotatingFileHandler(
            'logs/nash_energy_tickets.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
    else:
        app.logger.setLevel(logging.DEBUG)


def _seed_admin_user(app):
    from app.models import User, UserRole

    admin_email    = os.environ.get('ADMIN_EMAIL',    'admin@nashenergy.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@1234!')

    existing_admin = User.query.filter_by(email=admin_email).first()
    if not existing_admin:
        admin = User(
            full_name   = 'System Administrator',
            employee_id = 'ADMIN-001',
            email       = admin_email,
            department  = 'IT',
            role        = UserRole.ADMIN,
        )
        admin.password = admin_password
        db.session.add(admin)
        db.session.commit()
        app.logger.warning(
            f'[SEED] Default admin created: {admin_email} — CHANGE THIS PASSWORD IMMEDIATELY.'
        )
