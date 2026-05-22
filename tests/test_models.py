"""
Basic model tests for IT Ticketing System.
Run with: pytest tests/
"""

import pytest
from app import create_app
from app.extensions import db
from app.models import User, Ticket, UserRole, TicketPriority, TicketStatus


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


class TestUserModel:

    def test_password_hashing(self, app):
        with app.app_context():
            user = User(
                full_name='Test User',
                employee_id='TEST-001',
                email='test@company.com',
                role=UserRole.STAFF
            )
            user.password = 'SecurePass123'
            assert user.check_password('SecurePass123') is True
            assert user.check_password('WrongPassword') is False

    def test_password_not_readable(self, app):
        with app.app_context():
            user = User(
                full_name='Test User',
                employee_id='TEST-002',
                email='test2@company.com',
                role=UserRole.STAFF
            )
            user.password = 'SecurePass123'
            with pytest.raises(AttributeError):
                _ = user.password

    def test_admin_role(self, app):
        with app.app_context():
            admin = User(
                full_name='Admin User',
                employee_id='ADMIN-001',
                email='admin@company.com',
                role=UserRole.ADMIN
            )
            admin.password = 'AdminPass123'
            assert admin.is_admin is True
            assert admin.is_staff is False


class TestTicketModel:

    def test_ticket_creation(self, app):
        with app.app_context():
            ticket = Ticket(
                submitter_name='John Doe',
                submitter_employee_id='EMP-001',
                submitter_department='Engineering',
                submitter_email='john@company.com',
                problem_description='My laptop screen is flickering constantly.',
                priority=TicketPriority.HIGH,
                status=TicketStatus.OPEN,
            )
            db.session.add(ticket)
            db.session.commit()
            assert ticket.id is not None
            assert ticket.status == TicketStatus.OPEN

    def test_mark_solved_requires_remark(self, app):
        with app.app_context():
            admin = User(
                full_name='Admin',
                employee_id='ADMIN-001',
                email='admin@company.com',
                role=UserRole.ADMIN
            )
            admin.password = 'AdminPass123'
            db.session.add(admin)

            ticket = Ticket(
                submitter_name='Jane Doe',
                submitter_employee_id='EMP-002',
                submitter_department='Finance',
                submitter_email='jane@company.com',
                problem_description='Cannot access the financial reporting tool.',
                priority=TicketPriority.MEDIUM,
                status=TicketStatus.OPEN,
            )
            db.session.add(ticket)
            db.session.commit()

            with pytest.raises(ValueError):
                ticket.mark_solved(resolved_by_user=admin, remark='')
