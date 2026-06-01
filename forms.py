from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, EmailField, FileField, BooleanField, SelectField, FloatField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length, NumberRange, Optional
from flask_wtf.file import FileRequired, FileAllowed
from sqlalchemy import ForeignKey, select, DateTime
from extenstions import db
from models import User

#Saw the requirements of docstrings/typehints so here I am adding them

'''Form for users to edit their settings, pretty self explanatory'''

class EditSettingsForm(FlaskForm):
    name = StringField('Name')
    email = EmailField('Email')  #I mean do I reeeeeally need them to be able to edit the email
    password1 = PasswordField('Password')
    password2 = PasswordField('Password',validators=[EqualTo('password1')])
    bio = StringField('Bio')
    profile_pic = FileField('ProfilePicture')
    is_teacher = BooleanField('Teacher', default=False)  #at home dont forget to check this sht
    submit = SubmitField('edit')


    '''here they can select their timezones if they wish to change it, 
    if they dont select one UTC-o would automatically be the default one'''

    timezone = SelectField('Timezone', choices=[
            ('UTC', 'UTC±00:00'),
            ('America/New_York', 'UTC-05:00 (New York)'),
            ('America/Chicago', 'UTC-06:00 (Chicago)'),
            ('America/Denver', 'UTC-07:00 (Denver)'),
            ('America/Los_Angeles', 'UTC-08:00 (Los Angeles)'),
            ('Pacific/Honolulu', 'UTC-10:00 (Hawaii)'),
            ('Europe/London', 'UTC+00:00 (London)'),
            ('Europe/Paris', 'UTC+01:00 (Paris)'),
            ('Europe/Istanbul', 'UTC+03:00 (Istanbul)'),
            ('Asia/Dubai', 'UTC+04:00 (Dubai)'),
            ('Asia/Karachi', 'UTC+05:00 (Pakistan)'),
            ('Asia/Kolkata', 'UTC+05:30 (India)'),
            ('Asia/Dhaka', 'UTC+06:00 (Bangladesh)'),
            ('Asia/Bangkok', 'UTC+07:00 (Bangkok)'),
            ('Asia/Shanghai', 'UTC+08:00 (Beijing)'),
            ('Asia/Tokyo', 'UTC+09:00 (Tokyo)'),
            ('Australia/Sydney', 'UTC+10:00 (Sydney)'),
            ('Pacific/Auckland', 'UTC+12:00 (Auckland)')
        ], default='UTC')
    

    def validate_email(self, field):
        stmt = select(User).where(User.email == field.data)
        if db.session.execute(stmt).scalar_one_or_none():
            raise ValidationError('Email is taken.')  

class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password1 = PasswordField('Password',validators=[DataRequired()])
    password2 = PasswordField('Password',validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('signup')

    def validate_email(self, field):
        
        stmt = select(User).where(User.email == field.data)
        if db.session.execute(stmt).scalar_one_or_none():
            raise ValidationError('Email is taken.')
        


class SignInForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('sign in')


class MakePostForm(FlaskForm): 
    text = StringField('Text') 
    post_image = FileField('Image', validators = [FileRequired()])
    submit = SubmitField('Upload')


class ReviewForm(FlaskForm):
    comment = StringField('Comment', validators=[DataRequired()])
    rating = FloatField('Rating', validators=[DataRequired()])
    submit = SubmitField('Send')


class MakeSessForm(FlaskForm):
    skill_id = SelectField('Skill', coerce= int ,validators=[DataRequired()])
    start_date = StringField('Date', validators=[DataRequired()])
    start_time = StringField('Start Time', validators=[DataRequired()])
    end_time = StringField('End Time', validators=[DataRequired()])
    recurring = BooleanField('Repeat Weekly')
    weeks_count = IntegerField('Count of weeks', default=1)
    hourly_rate = FloatField('Hourly Rate', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Create Session')



class SessionRequestForm(FlaskForm):
    student_level = SelectField('Your Level', choices=[
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced')
    ], validators=[DataRequired()])
    student_goals = StringField('Your Goals', validators=[DataRequired()])
    submit = SubmitField('Send Request')

class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Permanently Delete My Account')