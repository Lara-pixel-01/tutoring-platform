import random
from typing import List, Optional as OptionalTip
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, select, DateTime


from flask_session import Session 
from flask.views import MethodView

from authlib.integrations.flask_client import OAuth

from flask_restful import Api, Resource
from pydantic import BaseModel

from models import User, Skill, user_skills, SessionRequest, Sess, Review, PortfolioPosts, Message, Notification

from extenstions import db

from flask_bcrypt import Bcrypt

from forms import *


bcrypt = None


class MainPageView(MethodView):   #note to self: later make this into a page where courses are displayed
    def get(self):
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
        
        user = db.session.execute(select(User).where(User.id== user_id)).scalar_one_or_none()


        form = MakeSessForm()
        form.skill_id.choices = [(skill.id, skill.name) for skill in user.skills]

        return render_template('create_session.html', form=form)
    
    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('signup'))
        
        user = db.session.execute(select(User).where(User.id== user_id)).scalar_one_or_none()
        
        form = MakeSessForm()
        form.skill_id.choices = [(skill.id, skill.name) for skill in user.skills]

        if form.validate_on_submit():

            start_time = datetime.fromisoformat(form.start_time.data)
            end_time = datetime.fromisoformat(form.end_time.data)

            sess = Sess(
                teacher_id= user_id,
                skill_id = form.skill_id.data,
                start_time=start_time,
                end_time=end_time,
                hourly_rate = form.hourly_rate.data
            )

            if user.is_teacher != True:
                user.is_teacher = True


            db.session.add(sess)
            db.session.commit()

            return redirect(url_for('dashboard'))
        
        return render_template('create_session.html', form=form)
