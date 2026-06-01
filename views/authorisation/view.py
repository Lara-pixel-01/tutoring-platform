import random
from typing import List, Optional as OptionalTip
from datetime import datetime, timedelta
from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, select, DateTime,func, delete

from authlib.integrations.flask_client import OAuth

from flask_restful import Api, Resource
from pydantic import BaseModel

from models import User, Skill, user_skills, SessionRequest, Sess, Review, PortfolioPosts, Message, Notification, UserSettings

from flask_bcrypt import Bcrypt

from forms import *

from base import BaseMethodView
from flask_login import login_user, current_user, login_required, logout_user

from views import bcrypt



class SignUpView(BaseMethodView):
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
            
            self.engine.session.add(user)
            self.engine.session.commit()

            settings = UserSettings(user_id =user.id)
            self.engine.session.add(settings)
            self.engine.session.commit() 

            login_user(user)

            return redirect(url_for('ind'))
        return render_template('signup.html', form = form)



class SignInView(BaseMethodView):
    def get(self):
        form = SignInForm()
        return render_template('signin.html', form=form)
    
    def post(self):
        form = SignInForm()
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            
            stmt = select(User).where(User.email == email)
            user = self.engine.session.execute(stmt).scalar_one_or_none()

            if user is None:
                return redirect(url_for('signup'))
            
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('ind'))
            
            return redirect(url_for('signin'))
        
        return render_template('signin.html', form=form)
    

class LogoutView(BaseMethodView):
    def get(self):
        logout_user()
        return redirect(url_for('ind'))