"""
Public ticket submission form.
Submitter details are auto-filled from the logged-in user account.
Only ticket-specific fields are shown.
"""
import bleach
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Optional

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'log']

PRIORITIES = [
    ('',       '-- Select Priority --'),
    ('Low',    'Low    — Minor issue, no immediate impact'),
    ('Medium', 'Medium — Moderate impact, needs attention'),
    ('High',   'High   — Critical issue, blocking work'),
]

CATEGORIES = [
    ('',            '-- Select Category --'),
    ('Hardware',    '💻  Hardware'),
    ('Software',    '🖥️  Software'),
    ('Network',     '🌐  Network'),
    ('CCTV',        '📷  CCTV'),
    ('Application', '📱  Application'),
]

APPLICATION_SUBCATEGORIES = [
    ('',           '-- Select Sub-Category --'),
    ('SAP',        'SAP'),
    ('Production', 'Production'),
    ('Planning',   'Planning'),
    ('MES',        'MES'),
]


class TicketSubmissionForm(FlaskForm):

    category = SelectField('Category', choices=CATEGORIES, validators=[
        DataRequired(message='Please select a category.'),
    ])

    sub_category = SelectField('Sub-Category', choices=APPLICATION_SUBCATEGORIES, validators=[
        Optional(),
    ])


    asset_id = StringField('Asset ID', validators=[
        Optional(),
        Length(min=3, max=100,
               message='Asset ID must be between 3 and 100 characters.'),
        Regexp(r'^[A-Za-z0-9\-]+$',
               message='Asset ID can only contain letters, numbers, and hyphens.'),
    ])

    priority = SelectField('Priority', choices=PRIORITIES, validators=[
        DataRequired(message='Please select a priority level.'),
    ])

    problem_description = TextAreaField('Problem Description', validators=[
        DataRequired(message='Please describe your issue.'),
        Length(min=20, max=5000,
               message='Description must be between 20 and 5000 characters.'),
    ])

    attachment = FileField('Attach Screenshot / File (Optional)', validators=[
        FileAllowed(ALLOWED_EXTENSIONS,
                    message=f'Allowed file types: {", ".join(ALLOWED_EXTENSIONS)}'),
    ])

    submit = SubmitField('Submit Ticket')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        if self.category.data == 'Application' and not self.sub_category.data:
            self.sub_category.errors.append('Please select a sub-category for Application.')
            return False
        return True
    

    def sanitize(self):
        self.problem_description.data = bleach.clean(
            self.problem_description.data.strip(), tags=[], strip=True)
        if self.asset_id.data:
            self.asset_id.data = bleach.clean(
                self.asset_id.data.strip(), tags=[], strip=True)
        if self.sub_category.data:
            self.sub_category.data = bleach.clean(
                self.sub_category.data.strip(), tags=[], strip=True)