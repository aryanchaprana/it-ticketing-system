import bleach
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class StartProgressForm(FlaskForm):
    estimated_resolution_time = StringField('Estimated Time to Resolve', validators=[
        DataRequired(message='Please provide an estimated resolution time.'),
        Length(min=2, max=200, message='Must be between 2 and 200 characters.'),
    ])
    submit = SubmitField('Mark as In Progress')

    def sanitize(self):
        self.estimated_resolution_time.data = bleach.clean(
            self.estimated_resolution_time.data.strip(), tags=[], strip=True)


class ResolveTicketForm(FlaskForm):

    resolution_remark = TextAreaField('Resolution Remark', validators=[
        DataRequired(message='Please describe how you resolved the issue.'),
        Length(min=10, max=2000,
               message='Remark must be between 10 and 2000 characters.'),
    ])

    submit = SubmitField('Mark as Solved')

    def sanitize(self):
        self.resolution_remark.data = bleach.clean(
            self.resolution_remark.data.strip(), tags=[], strip=True)
