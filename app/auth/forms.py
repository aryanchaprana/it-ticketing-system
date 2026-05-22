from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):

    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Enter a valid email address.'),
        Length(max=254),
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=8, max=128),
    ])

    remember_me = BooleanField('Keep me logged in')

    submit = SubmitField('Log In')


class ChangePasswordForm(FlaskForm):
    """Used for first-login forced password change and voluntary change."""

    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Please enter your current password.'),
    ])

    new_password = PasswordField('New Password', validators=[
        DataRequired(message='Please enter a new password.'),
        Length(min=8, message='Password must be at least 8 characters.'),
    ])

    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password.'),
        EqualTo('new_password', message='Passwords must match.'),
    ])

    submit = SubmitField('Change Password')
