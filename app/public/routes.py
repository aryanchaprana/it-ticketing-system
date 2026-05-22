"""
Public Blueprint — ticket submission (login required).
"""

import os
import uuid
from datetime import datetime, timezone

from flask import (Blueprint, render_template, redirect,
                   url_for, flash, current_app, send_from_directory, abort)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Ticket, TicketPriority, TicketStatus, TicketCategory
from app.public.forms import TicketSubmissionForm
from app.email_service.notifications import send_ticket_raised_email

public_bp = Blueprint('public', __name__, template_folder='../templates/public')


def _allowed_file(filename: str) -> bool:
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', set())
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def _save_attachment(file_storage):
    if not file_storage or file_storage.filename == '':
        return None, None
    original_name = file_storage.filename
    safe_name     = secure_filename(original_name)
    unique_name   = f"{uuid.uuid4().hex}_{safe_name}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    full_path = os.path.join(upload_folder, unique_name)
    file_storage.save(full_path)
    # Store only filename — avoids Windows backslash issue in URLs
    return unique_name, original_name


@public_bp.route('/')
def index():
    """Landing page — redirect logged-in users to their dashboard."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_staff:
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('employee.dashboard'))
    return render_template('public/index.html')


@public_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_ticket():
    """
    Ticket submission — requires login.
    Submitter details auto-filled from current_user account.
    """
    form = TicketSubmissionForm()

    if form.validate_on_submit():
        form.sanitize()

        # Asset ID mandatory for all except Network
        if form.category.data != 'Network' and not form.asset_id.data:
            flash('Asset ID is required for Hardware, Software, CCTV, and Application categories.', 'danger')
            return render_template('public/submit_ticket.html', form=form)

        # File attachment
        attachment_path, attachment_original_name = None, None
        if form.attachment.data and form.attachment.data.filename:
            if _allowed_file(form.attachment.data.filename):
                attachment_path, attachment_original_name = _save_attachment(
                    form.attachment.data)
            else:
                flash('Invalid file type.', 'danger')
                return render_template('public/submit_ticket.html', form=form)

        priority_map = {
            'Low':    TicketPriority.LOW,
            'Medium': TicketPriority.MEDIUM,
            'High':   TicketPriority.HIGH,
        }
        category_map = {
            'Hardware': TicketCategory.HARDWARE,
            'Software': TicketCategory.SOFTWARE,
            'Network':  TicketCategory.NETWORK,
            'CCTV':     TicketCategory.CCTV,
            'Application': TicketCategory.APPLICATION,
        }

        ticket = Ticket(
            # Link to the logged-in user account
            created_by_id            = current_user.id,
            # Snapshot of submitter info from their account
            submitter_name           = current_user.full_name,
            submitter_employee_id    = current_user.employee_id,
            submitter_department     = current_user.department or 'Not specified',
            submitter_email          = current_user.email,
            # Ticket details
            category                 = category_map.get(form.category.data),
            asset_id                 = form.asset_id.data or None,
            sub_category             = form.sub_category.data if form.category.data == 'Application' else None,
            problem_description      = form.problem_description.data,
            priority                 = priority_map.get(form.priority.data, TicketPriority.MEDIUM),
            status                   = TicketStatus.OPEN,
            attachment_path          = attachment_path,
            attachment_original_name = attachment_original_name,
            submitted_at             = datetime.now(timezone.utc),
        )

        db.session.add(ticket)
        db.session.commit()

        current_app.logger.info(
            f'Ticket {ticket.ticket_ref} submitted by '
            f'{current_user.employee_id} ({current_user.email})'
        )

        # Notify IT admin inbox that a new ticket has been raised
        send_ticket_raised_email(ticket)

        flash(f'Ticket submitted successfully! Reference: {ticket.ticket_ref}', 'success')
        return redirect(url_for('public.ticket_confirmation',
                                ticket_ref=ticket.ticket_ref))

    return render_template('public/submit_ticket.html', form=form)


@public_bp.route('/confirmation/<ticket_ref>')
@login_required
def ticket_confirmation(ticket_ref: str):
    ticket = Ticket.query.filter_by(ticket_ref=ticket_ref).first_or_404()
    return render_template('public/confirmation.html', ticket=ticket)


@public_bp.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename: str):
    """Serve uploaded files securely — login required."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    safe_name     = secure_filename(filename)

    if not safe_name:
        abort(404)

    return send_from_directory(
        directory=os.path.abspath(upload_folder),
        path=safe_name,
    )
