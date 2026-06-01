from typing import List, Optional as OptionalTip
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, select, DateTime,func, delete


from models import User, Skill, user_skills, SessionRequest, Sess, Review, PortfolioPosts, Message, Notification, UserSettings

from forms import MakePostForm, EditSettingsForm, DeleteAccountForm 

from base import BaseMethodView
from flask_login import login_user, current_user, login_required, logout_user

from werkzeug.utils import secure_filename
from pathlib import Path

from views import bcrypt


class UserPage(BaseMethodView): # ı need to detail this later still need to think how the html template would look like
    def get(self, user_id):
        user_profile = self.engine.session.execute(
            select(User).where(User.id == user_id)
            ).scalar_one_or_none()

        if user_profile is None:
            flash('User nto found', 'error')
            return redirect(url_for('ind'))
        
        available_sessions = []

        if user_profile.is_teacher:
            now = datetime.now()
            available_sessions = self.engine.session.execute(
                select(Sess).where(Sess.teacher_id == user_id, 
                                   Sess.status=='free',
                                   Sess.start_time > now)
                                   .order_by(Sess.start_time)
            ).scalars().all()

            for s in available_sessions:
                skill = self.engine.session.execute(
                    select(Skill).where(Skill.id == s.skill_id)
                ).scalar_one_or_none()
                s.skill = skill

        

        portfolio =  self.engine.session.execute(
            select(PortfolioPosts).where(PortfolioPosts.user_id == user_id)
            ).scalars().all()
        
        form = MakePostForm()
        

        return render_template('userpage.html', portfolio=portfolio, user_profile=user_profile, form=form, available_sessions=available_sessions)
    


    @login_required
    def post(self, user_id):
        if current_user.id != user_id:
            flash('You cant upload on someone elses profile')
            return redirect(url_for('user_page', user_id = user_id))
        
        form = MakePostForm()

        if form.validate_on_submit():
            filename = None

            if form.post_image.data:
                filename = secure_filename(f"{current_user.id}_{form.post_image.data.filename}")
                upload_path = Path('static/uploads')
                upload_path.mkdir(parents=True, exist_ok=True)

                form.post_image.data.save(upload_path / filename)

            post = PortfolioPosts(
                user_id=current_user.id,
                text=form.text.data or "",
                image=filename
            )
            self.engine.session.add(post)
            self.engine.session.commit()

            flash('New post is added', 'success')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')

        return redirect(url_for('user_page', user_id=user_id))



class EditSettingView(BaseMethodView):
    @login_required
    def get(self):
        form = EditSettingsForm()
        delete_form = DeleteAccountForm()
        return render_template('settings.html', form=form, delete_form=delete_form)
    
    @login_required
    def post(self):
        user= current_user
        form = EditSettingsForm()
        delete_form = DeleteAccountForm()
        user = self.engine.session.execute(select(User).where(User.id == current_user.id)).scalar()


        if form.validate_on_submit():
            if form.name.data:
                user.name = form.name.data

            if form.email.data:
                user.email = form.email.data
            
            if form.password1.data:
                user.password = bcrypt.generate_password_hash(form.password1.data).decode('utf-8')

            if form.bio.data:
                user.bio = form.bio.data

            timezone_value = form.timezone.data
            if timezone_value:
                user_settings = self.engine.session.get(UserSettings, user.id)
                if not user_settings:
                    user_settings = UserSettings(user_id=user.id)
                    self.engine.session.add(user_settings)
                user_settings.timezone = timezone_value
            
            user.is_teacher = form.is_teacher.data
            self.engine.session.commit()

            return redirect(url_for('ind'))
        
        return render_template('settings.html', form=form, delete_form=delete_form)
    

class DeleteAccountView(BaseMethodView):
    @login_required
    def post(self):
        form = DeleteAccountForm()
        
        if form.validate_on_submit():
            user = self.engine.session.get(User, current_user.id)
            
            if not bcrypt.check_password_hash(user.password, form.password.data):
                flash('Incorrect password', 'error')
                return redirect(url_for('settings'))
            
            
            self.engine.session.execute(
                delete(SessionRequest).where(SessionRequest.session.has(Sess.teacher_id == user.id))
            )
            self.engine.session.execute(
                delete(SessionRequest).where(SessionRequest.student_id == user.id)
            )
        
            self.engine.session.execute(
                delete(Sess).where(Sess.teacher_id == user.id)
            )
            self.engine.session.execute(
                delete(Sess).where(Sess.student_id == user.id)
            )
            self.engine.session.execute(
                delete(Review).where(Review.reviewer_id == user.id)
            )
            self.engine.session.execute(
                delete(Review).where(Review.teacher_id == user.id)
            )
    
            self.engine.session.execute(
                delete(Message).where(Message.sender_id == user.id)
            )
            self.engine.session.execute(
                delete(Message).where(Message.receiver_id == user.id)
            )
        
            self.engine.session.execute(
                delete(Notification).where(Notification.user_id == user.id)
            )
            self.engine.session.execute(
                delete(PortfolioPosts).where(PortfolioPosts.user_id == user.id)
            )
        
            self.engine.session.execute(
                delete(UserSettings).where(UserSettings.user_id == user.id)
            )
            self.engine.session.delete(user)
            self.engine.session.commit()
            
            logout_user()
            flash('Your account has been permanently deleted', 'info')
            return redirect(url_for('ind'))
        
        flash('Invalid submission', 'error')
        return redirect(url_for('settings'))