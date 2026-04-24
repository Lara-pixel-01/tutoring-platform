from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, EmailField, FileField, BooleanField, SelectField, FloatField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length, NumberRange, Optional
from flask_wtf.file import FileRequired, FileAllowed
from sqlalchemy import ForeignKey, select, DateTime
from extenstions import db
from models import User



class EditSettingsForm(FlaskForm):
    name = StringField('Name')
    email = EmailField('Email')  #I mean do I reeeeeally need them to be able to edit the email
    password1 = PasswordField('Password')
    password2 = PasswordField('Password',validators=[EqualTo('password1')])
    bio = StringField('Bio')
    profile_pic = FileField('ProfilePicture')
    is_teacher = BooleanField('Teacher', default=False)  #at home dont forget to check this sht
    submit = SubmitField('edit')

    def validate_email(self, field):
        stmt = select(User).where(User.email == field.data)
        if db.session.execute(stmt).scalar_one_or_none():
            raise ValidationError('Email is taken.')  #note to self we we need to store files as links


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


class MakePostForm(FlaskForm): #for commmentrs I need to add something else ig
    text = StringField('Text')  #this can be optional ig
    post_image = FileField('Image', validators = [FileRequired()])
    submit = SubmitField('Upload')


class ReviewForm(FlaskForm): # NOT DONE!!!! Finish this later with template, view etc
    comment = StringField('Comment', validators=[DataRequired()])
    rating = IntegerField('Rating', validators=[DataRequired()])
    submit = SubmitField('Send')


class MakeSessForm(FlaskForm):
    skill_id = SelectField('Skill', coerce= int ,validators=[DataRequired()])
    start_time = StringField('Start Time', validators=[DataRequired()])
    end_time = StringField('End Time', validators=[DataRequired()])
    hourly_rate = FloatField('Hourly Rate', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Create Session')