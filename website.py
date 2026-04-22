import random
from typing import List, Optional as OptionalTip
from faker import Faker
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, select, DateTime


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, EmailField, FileField, BooleanField, SelectField, FloatField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length, NumberRange, Optional
from flask_wtf.file import FileRequired, FileAllowed
    

from flask_session import Session 
from flask.views import MethodView

from authlib.integrations.flask_client import OAuth

from flask_restful import Api, Resource
from pydantic import BaseModel

from models import User, Skill, user_skills, SessionRequest, Sess, Review, PortfolioPosts, Message, Notification, db

from flask_bcrypt import Bcrypt


fake = Faker()


SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:ash123@localhost:5432/skillPlatform'
SECRET_KEY = "hnDsdfjsSdfINFBVNWDVN232342342341dfsdfsfsd567cgvhjbvgcdrt4567SDSFGFBVDFthfgbv"
SESSION_TYPE = 'filesystem'

app = Flask(__name__)

bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_TYPE'] = SESSION_TYPE

app.config['WTF_CSRF_ENABLED'] = True

Session(app)

db.init_app(app)


#FORM AREA(REMINDER TO SELF TO SEPERATE THESE LATER CAUSE TOO CROWDED ALREADY)================================

#note to self make a edit profile attributes for users, maybe profile table might needed to be added. or not we will see :D


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



#this is for testing purposes:
def generate_data_for_db():  
    with app.app_context():   
        db.drop_all()
        db.create_all()


        skill_cat = {
            "Programming": ['Python', 'Java', "SQL"],
            "Language": ['English', 'Japanese', 'Chinese'],
            "Maths": ['Algebra', 'Calculus', 'Statistics','Probability']
        }
        
        for category, skill in skill_cat.items():
            for name in skill:
                user_skill = Skill(
                    name=name,
                    category=category
                )
                db.session.add(user_skill)
        db.session.commit()


            
        for i in range(20):
            user = User(email= fake.email(),
                password = bcrypt.generate_password_hash(fake.password()).decode('utf-8'),
                name = fake.name(),
                bio = fake.paragraph(nb_sentences=random.randint(3, 7)),
                is_teacher = fake.boolean()
            )

            db.session.add(user)
        db.session.commit()

        teachers = db.session.execute(select(User).where(User.is_teacher==True)).scalars().all()

        skills = db.session.execute(select(Skill)).scalars().all()

        for teacher in teachers:
            skill_count =  random.randint(1,3)
            teacher_skill = random.sample(skills, skill_count)
            teacher.skills.extend(teacher_skill)
        
        db.session.commit()



        for teacher in teachers:
            users  =  db.session.execute(select(User).where(User.id != teacher.id)).scalars().all()
            review_count = random.randint(3,10)

            reviewers = random.sample(users, min(review_count, len(users)))

            for reviewer in reviewers:
                review = Review(
                    comment = fake.paragraph(nb_sentences=random.randint(1,3)),
                    reviewer_id = reviewer.id,
                    teacher_id = teacher.id,
                    rating = random.choice([3.5, 3, 4, 5, 4.5])
                )
                db.session.add(review)
        
        db.session.commit()




#VIEWS ========================================================================================================





class MainPageView(MethodView):   #note to self: later make this into a page where courses are displayed
    def get(self):
        with app.app_context():
            stmt = select(User).where(User.is_teacher == True)
            teachers = db.session.execute(stmt).scalars().all()

            if len(teachers) >= 6:
                random_teachers = random.sample(teachers, 6)
            else:
                random_teachers = teachers
            
            user_id = session.get('user_id')
            user = None
            if user_id:
                user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            
            return render_template('mainpage.html', users= random_teachers, user=user)

    

class SignUpView(MethodView):
    def get(self):
        form = SignUpForm() 
        return render_template('signup.html', form = form)
    
    def post(self):
        form = SignUpForm() 
        if form.validate_on_submit():
            password_hashed = bcrypt.generate_password_hash(form.password1.data).decode('utf-8')

            user = User(email=form.email.data,
                        password=password_hashed, 
                        name=form.name.data,
                        )
            db.session.add(user)
            db.session.commit() 

            session["user_id"] = user.id

            return redirect(url_for('ind'))
        return render_template('signup.html', form = form)


class SignInView(MethodView):
    def get(self):
        form = SignInForm()
        return render_template('signin.html', form=form)
    
    def post(self):
        form = SignInForm()
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            
            stmt = select(User).where(User.email == email)
            user = db.session.execute(stmt).scalar_one_or_none()

            if user is None:
                return redirect(url_for('signup'))
            
            if bcrypt.check_password_hash(user.password, password):
                session["user_id"] = user.id
                return redirect(url_for('ind'))
            
            return redirect(url_for('signin'))
        
        return render_template('signin.html', form=form)
    

class EditSettingView(MethodView):
    def get(self):
        user_id = session.get('user_id')  
        if not user_id:
            return redirect(url_for('signin')) 
        
        form = EditSettingsForm()
        return render_template('settings.html', form=form)
    
    def post(self):
        user_id = session.get('user_id')  #needs to be edited so I can #continue your sentence I have no idea wtf I wrote here forgot
        if not user_id:
            return redirect(url_for('signin'))

        form = EditSettingsForm()
        user = db.session.execute(select(User).where(User.id == user_id)).scalar()


        if form.validate_on_submit():
            if form.name.data:
                user.name = form.name.data

            if form.email.data:
                user.email = form.email.data
            
            if form.password1.data:
                user.password = bcrypt.generate_password_hash(form.password1.data).decode('utf-8')

            if form.bio.data:
                user.bio = form.bio.data
            
            user.is_teacher = form.is_teacher.data
            
            db.session.commit()

            return redirect(url_for('ind'))
        return render_template('settings.html', form=form)
    

class UserProfileView(MethodView):
    def get(self):
        return render_template('user_profile.html')

    

class UserDashboardView(MethodView):
    def get(self):

        user_id = session.get('user_id')  
        if user_id is None:
            return redirect(url_for('signin'))
        
        user = db.session.execute(select(User).where(User.id == user_id)).scalar()
        
        return render_template('dashboard.html', user = user)
    

class LogoutView(MethodView):
    def get(self):
        session.clear()
        return redirect(url_for('ind'))
    

class UserPage(MethodView): # ı need to detail this later still need to think how the html template would look like
    def get(self):
        pass
    
    def post(self):
        pass #need to make a page




class ReviewView(MethodView): 
    def get(self, teacher_id):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('signup'))
        
        form = ReviewForm()
        return render_template('review.html', form=form)
    
    def post(self, teacher_id):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('signup'))
        
        form = ReviewForm()

        if form.validate_on_submit():
            review = Review(
                comment= form.comment.data,
                reviewer_id = user_id,
                teacher_id=teacher_id,
                rating = form.rating.data
            )

            db.session.add(review)
            db.session.commit()
            
            return redirect(url_for('review'))
        
        return render_template('review.html', form = form)



class MakeSessView(MethodView):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('signup'))
        
        user = db.session.execute(select(User).where(User.id== user_id))

        skill_choises = [(skill.id, skill.name) for skill in user.skills]




            #Im tired :)...
            


app.add_url_rule('/', view_func=MainPageView.as_view('ind'))
app.add_url_rule('/signup/', view_func=SignUpView.as_view('signup'))
app.add_url_rule('/signin/', view_func=SignInView.as_view('signin'))
app.add_url_rule('/settings/', view_func=EditSettingView.as_view('settings'))
app.add_url_rule('/dashboard/', view_func=UserDashboardView.as_view('dashboard'))
app.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
app.add_url_rule('/review/<int:teacher_id>', view_func=ReviewView.as_view('review'))

if __name__ == '__main__':
	generate_data_for_db()
	print(app.url_map)
	app.run(port=9000, debug=True, use_reloader=False)