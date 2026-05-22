"""
SQLAlchemy Database Models for IT Ticketing System.
"""

import enum
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class UserRole(enum.Enum):
    ADMIN    = 'admin'
    STAFF    = 'staff'
    EMPLOYEE = 'employee'


class TicketPriority(enum.Enum):
    LOW    = 'Low'
    MEDIUM = 'Medium'
    HIGH   = 'High'


class TicketCategory(enum.Enum):
    HARDWARE = 'Hardware'
    SOFTWARE = 'Software'
    NETWORK  = 'Network'
    CCTV     = 'CCTV'
    APPLICATION = 'Application'


class TicketStatus(enum.Enum):
    OPEN        = 'Open'
    ASSIGNED    = 'Assigned'
    IN_PROGRESS = 'In Progress'
    SOLVED      = 'Solved'
    CLOSED      = 'Closed'


# ---------------------------------------------------------------------------
# User Model
# ---------------------------------------------------------------------------

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id             = db.Column(db.Integer, primary_key=True)
    full_name      = db.Column(db.String(120), nullable=False)
    employee_id    = db.Column(db.String(50),  unique=True, nullable=False, index=True)
    email          = db.Column(db.String(254), unique=True, nullable=False, index=True)
    department     = db.Column(db.String(100), nullable=True)
    _password_hash = db.Column('password_hash', db.String(256), nullable=False)
    role           = db.Column(
                       db.Enum(UserRole, name='user_role_enum'),
                       nullable=False,
                       default=UserRole.EMPLOYEE
                     )
    is_active            = db.Column(db.Boolean, default=True,  nullable=False)
    must_change_password = db.Column(db.Boolean, default=True,  nullable=False)
    created_at           = db.Column(db.DateTime(timezone=True),
                                     default=lambda: datetime.now(timezone.utc),
                                     nullable=False)
    last_login_at        = db.Column(db.DateTime(timezone=True), nullable=True)

    # Tickets this user submitted (as an employee)
    submitted_tickets = db.relationship(
        'Ticket',
        foreign_keys='Ticket.created_by_id',
        back_populates='created_by',
        lazy='dynamic'
    )
    # Tickets assigned to this IT staff member
    assigned_tickets = db.relationship(
        'Ticket',
        foreign_keys='Ticket.assigned_to_id',
        back_populates='assigned_to',
        lazy='dynamic'
    )
    # Tickets this user resolved
    solved_tickets = db.relationship(
        'Ticket',
        foreign_keys='Ticket.solved_by_id',
        back_populates='solved_by',
        lazy='dynamic'
    )

    @property
    def password(self):
        raise AttributeError('Password is write-only.')

    @password.setter
    def password(self, plaintext_password: str):
        if len(plaintext_password) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        self._password_hash = generate_password_hash(
            plaintext_password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, plaintext_password: str) -> bool:
        return check_password_hash(self._password_hash, plaintext_password)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_staff(self) -> bool:
        return self.role == UserRole.STAFF

    @property
    def is_employee(self) -> bool:
        return self.role == UserRole.EMPLOYEE

    def get_id(self) -> str:
        return str(self.id)

    def update_last_login(self):
        self.last_login_at = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            'id':          self.id,
            'full_name':   self.full_name,
            'employee_id': self.employee_id,
            'email':       self.email,
            'department':  self.department,
            'role':        self.role.value,
            'is_active':   self.is_active,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f'<User id={self.id} employee_id={self.employee_id!r} role={self.role.value}>'


# ---------------------------------------------------------------------------
# Ticket Model
# ---------------------------------------------------------------------------

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id         = db.Column(db.Integer, primary_key=True)
    ticket_ref = db.Column(db.String(20), unique=True, nullable=True, index=True)

    # Who raised this ticket (linked to their account)
    created_by_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    created_by = db.relationship('User', foreign_keys=[created_by_id],
                                 back_populates='submitted_tickets')

    # Submitter info (snapshot from account at time of submission)
    submitter_name        = db.Column(db.String(120), nullable=False)
    submitter_employee_id = db.Column(db.String(50),  nullable=False)
    submitter_department  = db.Column(db.String(100), nullable=False)
    submitter_email       = db.Column(db.String(254), nullable=False)

    # Category and Asset
    category = db.Column(
        db.Enum(TicketCategory, name='ticket_category_enum'),
        nullable=False,
        index=True
    )
    asset_id = db.Column(db.String(100), nullable=True)

    # Application sub-category (SAP, Production, Planning, MES)
    sub_category = db.Column(db.String(50), nullable=True)

    # Ticket content
    problem_description = db.Column(db.Text, nullable=False)
    priority = db.Column(
        db.Enum(TicketPriority, name='ticket_priority_enum'),
        nullable=False,
        default=TicketPriority.MEDIUM,
        index=True
    )

    # AI Integration Hook
    ai_suggested_priority = db.Column(db.String(20), nullable=True)
    ai_analysis_notes     = db.Column(db.Text,       nullable=True)

    # File attachment — stores filename only
    attachment_path          = db.Column(db.String(512), nullable=True)
    attachment_original_name = db.Column(db.String(255), nullable=True)

    # Status & resolution
    status = db.Column(
        db.Enum(TicketStatus, name='ticket_status_enum'),
        nullable=False,
        default=TicketStatus.OPEN,
        index=True
    )
    resolution_remark = db.Column(db.Text, nullable=True)
    estimated_resolution_time = db.Column(db.String(200), nullable=True)

    # Preferred IT staff chosen by submitter
    preferred_staff_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )
    preferred_staff = db.relationship('User', foreign_keys=[preferred_staff_id])

    # Timeline timestamps
    submitted_at   = db.Column(db.DateTime(timezone=True),
                               default=lambda: datetime.now(timezone.utc),
                               nullable=False, index=True)
    assigned_at    = db.Column(db.DateTime(timezone=True), nullable=True)
    in_progress_at = db.Column(db.DateTime(timezone=True), nullable=True)
    updated_at     = db.Column(db.DateTime(timezone=True),
                               default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc),
                               nullable=False)
    solved_at      = db.Column(db.DateTime(timezone=True), nullable=True)

    # Foreign keys
    assigned_to_id = db.Column(db.Integer,
                               db.ForeignKey('users.id', ondelete='SET NULL'),
                               nullable=True, index=True)
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id],
                                  back_populates='assigned_tickets')

    solved_by_id = db.Column(db.Integer,
                             db.ForeignKey('users.id', ondelete='SET NULL'),
                             nullable=True)
    solved_by = db.relationship('User', foreign_keys=[solved_by_id],
                                back_populates='solved_tickets')

    def mark_solved(self, resolved_by_user, remark: str):
        if not remark or not remark.strip():
            raise ValueError('A resolution remark is required to solve a ticket.')
        if self.status in (TicketStatus.SOLVED, TicketStatus.CLOSED):
            raise ValueError(f'Ticket is already {self.status.value}.')
        self.status            = TicketStatus.SOLVED
        self.resolution_remark = remark.strip()
        self.solved_by_id      = resolved_by_user.id
        self.solved_at         = datetime.now(timezone.utc)
        self.updated_at        = datetime.now(timezone.utc)

    def assign_to(self, staff_user):
        if not staff_user.is_active:
            raise ValueError(f'Cannot assign to inactive user {staff_user.employee_id}.')
        self.assigned_to_id = staff_user.id
        self.status         = TicketStatus.ASSIGNED
        self.assigned_at    = datetime.now(timezone.utc)
        self.updated_at     = datetime.now(timezone.utc)

    @property
    def is_overdue(self) -> bool:
        if self.status in (TicketStatus.SOLVED, TicketStatus.CLOSED):
            return False
        if self.priority == TicketPriority.HIGH:
            delta = datetime.now(timezone.utc) - self.submitted_at
            return delta.total_seconds() > (4 * 3600)
        return False

    def to_dict(self) -> dict:
        return {
            'id':                       self.id,
            'ticket_ref':               self.ticket_ref,
            'created_by_id':            self.created_by_id,
            'submitter_name':           self.submitter_name,
            'submitter_employee_id':    self.submitter_employee_id,
            'submitter_department':     self.submitter_department,
            'submitter_email':          self.submitter_email,
            'category':                 self.category.value if self.category else None,
            'asset_id':                 self.asset_id,
            'sub_category':             self.sub_category,
            'problem_description':      self.problem_description,
            'priority':                 self.priority.value,
            'status':                   self.status.value,
            'resolution_remark':        self.resolution_remark,
            'attachment_path':          self.attachment_path,
            'attachment_original_name': self.attachment_original_name,
            'assigned_to_id':           self.assigned_to_id,
            'solved_by_id':             self.solved_by_id,
            'submitted_at':             self.submitted_at.isoformat() if self.submitted_at else None,
            'solved_at':                self.solved_at.isoformat()    if self.solved_at     else None,
            'is_overdue':               self.is_overdue,
        }

    def __repr__(self) -> str:
        return (f'<Ticket id={self.id} ref={self.ticket_ref!r} '
                f'status={self.status.value} priority={self.priority.value}>')


# ---------------------------------------------------------------------------
# Auto-generate ticket reference number after insert
# ---------------------------------------------------------------------------

from sqlalchemy import event

@event.listens_for(Ticket, 'after_insert')
def generate_ticket_ref(mapper, connection, target):
    connection.execute(
        Ticket.__table__.update()
        .where(Ticket.__table__.c.id == target.id)
        .values(ticket_ref=f'TKT-{target.id:05d}')
    )
