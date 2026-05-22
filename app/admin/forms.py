import bleach
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField,
                     TextAreaField, SubmitField, BooleanField)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional


class CreateUserForm(FlaskForm):
    """Creates IT Staff, Admin, or Employee accounts."""

    full_name = StringField('Full Name', validators=[
        DataRequired(), Length(min=2, max=120),
    ])

    employee_id = StringField('Employee ID', validators=[
        DataRequired(),
        Length(min=2, max=50),
        Regexp(r'^[A-Za-z0-9\-]+$',
               message='Employee ID: letters, numbers, and hyphens only.'),
    ])

    email = StringField('Email Address', validators=[
        DataRequired(), Email(), Length(max=254),
    ])

    department = SelectField('Department', choices=[
        ('', '-- Select --'),
        ('IT', 'IT'),
        ('Production', 'Production'),
        ('Pre-Assembly', 'Pre-Assembly'),
        ('Assembly', 'Assembly'),
        ('El-Filling', 'El-Filling'),
        ('Post-Assembly', 'Post-Assembly'),
        ('Testing', 'Testing'),
        ('Formation', 'Formation'),
        ('Dispatch Section', 'Dispatch Section'),
        ('Store', 'Store'),
        ('Quality', 'Quality'),
        ('Process Engineer', 'Process Engineer'),
        ('R&D', 'R&D'),
        ('Purchase', 'Purchase'),
        ('Battery Pack', 'Battery Pack'),
        ('Sales & Marketing', 'Sales & Marketing'),
        ('HR', 'HR'),
        ('COO', 'COO'),
        ('NPD', 'NPD'),
        ('SCM', 'SCM'),
        ('Maintainence', 'Maintainence'),
        ('EHS', 'EHS'),
        ('Costing', 'Costing'),
        ('PPC', 'PPC'),
        ('Stores', 'Stores'),
        ('Admin', 'Admin'),
    ], validators=[DataRequired()])

    role = SelectField('Role', choices=[
        ('employee', 'Employee — can only submit tickets'),
        ('staff',    'IT Staff — can resolve assigned tickets'),
        ('admin',    'IT Admin — full access'),
    ], validators=[DataRequired()])

    password = PasswordField('Temporary Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters.'),
    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.'),
    ])

    submit = SubmitField('Create Account')

    def sanitize(self):
        self.full_name.data   = bleach.clean(self.full_name.data.strip(),     tags=[], strip=True)
        self.employee_id.data = bleach.clean(self.employee_id.data.strip(),   tags=[], strip=True)
        self.email.data       = bleach.clean(self.email.data.strip().lower(), tags=[], strip=True)
        self.department.data  = bleach.clean(self.department.data.strip(),    tags=[], strip=True)


class AssignTicketForm(FlaskForm):
    assigned_to = SelectField('Assign To', coerce=int, validators=[
        DataRequired(message='Please select a staff member.'),
    ])
    submit = SubmitField('Assign Ticket')


class ChangePriorityForm(FlaskForm):
    priority = SelectField('New Priority', choices=[
        ('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'),
    ], validators=[DataRequired()])
    submit = SubmitField('Update Priority')


class SolveTicketForm(FlaskForm):
    resolution_remark = TextAreaField('Resolution Remark', validators=[
        DataRequired(message='A resolution remark is required.'),
        Length(min=10, max=2000),
    ])
    submit = SubmitField('Mark as Solved')

    def sanitize(self):
        self.resolution_remark.data = bleach.clean(
            self.resolution_remark.data.strip(), tags=[], strip=True)


class EditUserForm(FlaskForm):
    """Admin edits an existing user's profile details."""

    full_name = StringField('Full Name', validators=[
        DataRequired(), Length(min=2, max=120),
    ])

    employee_id = StringField('Employee ID', validators=[
        DataRequired(),
        Length(min=2, max=50),
        Regexp(r'^[A-Za-z0-9\-]+$',
               message='Employee ID: letters, numbers, and hyphens only.'),
    ])

    email = StringField('Email Address', validators=[
        DataRequired(), Email(), Length(max=254),
    ])

    department = SelectField('Department', choices=[
        ('', '-- Select --'),
        ('IT', 'IT'),
        ('Production', 'Production'),
        ('Pre-Assembly', 'Pre-Assembly'),
        ('Assembly', 'Assembly'),
        ('El-Filling', 'El-Filling'),
        ('Post-Assembly', 'Post-Assembly'),
        ('Testing', 'Testing'),
        ('Formation', 'Formation'),
        ('Dispatch Section', 'Dispatch Section'),
        ('Store', 'Store'),
        ('Quality', 'Quality'),
        ('Process Engineer', 'Process Engineer'),
        ('R&D', 'R&D'),
        ('Purchase', 'Purchase'),
        ('Battery Pack', 'Battery Pack'),
        ('Sales & Marketing', 'Sales & Marketing'),
        ('HR', 'HR'),
        ('COO', 'COO'),
        ('NPD', 'NPD'),
        ('SCM', 'SCM'),
        ('Maintainence', 'Maintainence'),
        ('EHS', 'EHS'),
        ('Costing', 'Costing'),
        ('PPC', 'PPC'),
        ('Stores', 'Stores'),
        ('Admin', 'Admin'),
    ], validators=[DataRequired()])

    role = SelectField('Role', choices=[
        ('employee', 'Employee — can only submit tickets'),
        ('staff',    'IT Staff — can resolve assigned tickets'),
        ('admin',    'IT Admin — full access'),
    ], validators=[DataRequired()])

    submit = SubmitField('Save Changes')

    def sanitize(self):
        self.full_name.data   = bleach.clean(self.full_name.data.strip(),     tags=[], strip=True)
        self.employee_id.data = bleach.clean(self.employee_id.data.strip(),   tags=[], strip=True)
        self.email.data       = bleach.clean(self.email.data.strip().lower(), tags=[], strip=True)
        self.department.data  = bleach.clean(self.department.data.strip(),    tags=[], strip=True)


class AdminResetPasswordForm(FlaskForm):
    """Admin resets a user's password and forces them to change it on next login."""

    new_password = PasswordField('New Temporary Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters.'),
    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.'),
    ])

    submit = SubmitField('Reset Password')
