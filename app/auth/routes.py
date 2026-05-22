"""
Auth Blueprint — login, logout, and password management.
"""

from flask import (Blueprint, render_template, redirect,
                   url_for, flash, request)
from flask_login import login_user, logout_user, login_required, current_user

import bleach

from app.extensions import db
from app.models import User, UserRole
from app.auth.forms import LoginForm, ChangePasswordForm

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')


def _redirect_by_role(user):
    """Send each role to their own dashboard after login."""
    if user.is_admin:
        return redirect(url_for('admin.dashboard'))
    elif user.is_staff:
        return redirect(url_for('staff.dashboard'))
    else:
        return redirect(url_for('employee.dashboard'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # If already logged in but must change password — enforce it
        if current_user.must_change_password:
            return redirect(url_for('auth.change_password'))
        return _redirect_by_role(current_user)

    form = LoginForm()

    if form.validate_on_submit():
        raw_email = bleach.clean(form.email.data.strip().lower(), tags=[], strip=True)
        user      = User.query.filter_by(email=raw_email).first()

        # Same message for wrong email OR wrong password — prevents user enumeration
        if not user or not user.check_password(form.password.data):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html', form=form)

        if not user.is_active:
            flash('Your account has been deactivated. Contact the IT Admin.', 'warning')
            return render_template('auth/login.html', form=form)

        login_user(user, remember=form.remember_me.data)
        user.update_last_login()

        # Force password change on first login
        if user.must_change_password:
            flash('Welcome! Please change your temporary password before continuing.', 'warning')
            return redirect(url_for('auth.change_password'))

        # Safe redirect — only follow internal URLs
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)

        return _redirect_by_role(user)

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Password change page.
    - Forced on first login (must_change_password = True)
    - Also accessible voluntarily from any dashboard
    """
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Your current password is incorrect.', 'danger')
            return render_template('auth/change_password.html', form=form,
                                   forced=current_user.must_change_password)

        # Set new password
        current_user.password            = form.new_password.data
        current_user.must_change_password = False
        db.session.commit()

        flash('Password changed successfully. Welcome!', 'success')
        return _redirect_by_role(current_user)

    return render_template('auth/change_password.html', form=form,
                           forced=current_user.must_change_password)
