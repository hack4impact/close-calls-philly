import datetime as datetime

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import (
    StringField,
    SubmitField,
    IntegerField,
    TextAreaField,
    HiddenField,
    DateField,
)
from wtforms_components import TimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import (
    InputRequired,
    Length,
    Optional,
    NumberRange,
    URL,
    Regexp,
)

from app.custom_validators import StrippedLength, ValidLocation, RequiredIf
from .. import db


class IncidentReportForm(Form):
    location = StringField('Address', validators=[
        InputRequired('Address is required.'),
        ValidLocation()
        ])

    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')

    automobile_num = IntegerField('Automobile', validators=[
        Optional()
    ])

    bicycle_num = IntegerField('Bicycle', validators=[
        Optional()
    ])

    pedestrian_num = IntegerField('Pedestrian', validators=[
        Optional()
    ])

    other_num = IntegerField('Other', validators=[
        Optional()
    ])

    today = datetime.datetime.today()

    date = DateField('Date (year-month-day)',
                     default=today.strftime('%m-%d-%Y'),
                     validators=[InputRequired()])

    time = TimeField('Time (hours:minutes am/pm)',
                     default=today.strftime('%I:%M %p'),
                     validators=[InputRequired()])

    picture_file = FileField(
        'Upload a photo (optional)',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp'],
                        'Only images are allowed.')
        ]
    )

    description = TextAreaField('Description', validators=[
        InputRequired(),
        Length(max=5000)
    ])

    injuries = TextAreaField('Injuries (optional)', validators=[
        Optional(),
        Length(max=5000)
    ])

    contact_name = StringField('Contact Name (optional)', validators=[
        Optional(),
        Length(max=1000)
    ])

    contact_phone = StringField('Contact Phone (optional)', validators=[
        Optional(),
        Length(max=1000)
    ])

    contact_email = StringField('Contact E-mail (optional)', validators=[
        Optional(),
        Length(max=100)
    ])

    submit = SubmitField('Create Report')


class EditIncidentReportForm(IncidentReportForm):
    duration = StringField('Idling Duration (h:m:s)', validators=[
        InputRequired('Idling duration is required.'),
        Regexp(r'^(\d{1,2}:)(\d{1,2}:)(\d{1,2})$',
               message='Write duration as HH:MM:SS')
    ])

    submit = SubmitField('Update Report')