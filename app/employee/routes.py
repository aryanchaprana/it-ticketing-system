"""
Employee Blueprint — regular employees can submit tickets and view their own history.
"""

from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import Ticket, TicketStatus, UserRole

employee_bp = Blueprint('employee', __name__, template_folder='../templates/employee')


def employee_required(f):
    """Allow employees, staff, and admin — block anyone not logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@employee_bp.route('/')
@login_required
@employee_required
def dashboard():
    """
    Employee dashboard — shows all tickets they have submitted
    with current status. Suggestion 2 implemented here.
    """
    tickets = Ticket.query.filter_by(
        created_by_id=current_user.id
    ).order_by(Ticket.submitted_at.desc()).all()

    # Summary counts
    stats = {
        'total':       len(tickets),
        'open':        sum(1 for t in tickets if t.status == TicketStatus.OPEN),
        'in_progress': sum(1 for t in tickets if t.status == TicketStatus.IN_PROGRESS),
        'solved':      sum(1 for t in tickets if t.status == TicketStatus.SOLVED),
    }

    return render_template('employee/dashboard.html', tickets=tickets, stats=stats)


@employee_bp.route('/ticket/<int:ticket_id>')
@login_required
@employee_required
def ticket_detail(ticket_id: int):
    """Employee views one of their own tickets — read only."""
    ticket = Ticket.query.get_or_404(ticket_id)

    # Employees can only see their own tickets
    if ticket.created_by_id != current_user.id:
        abort(403)

    return render_template('employee/ticket_detail.html', ticket=ticket)
