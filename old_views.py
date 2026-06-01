import random
from typing import List, Optional as OptionalTip
from datetime import datetime, timedelta
from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, select, DateTime,func, delete

from authlib.integrations.flask_client import OAuth

from flask_restful import Api, Resource
from pydantic import BaseModel

from models import User, Skill, user_skills, SessionRequest, Sess, Review, PortfolioPosts, Message, Notification

from flask_bcrypt import Bcrypt

from forms import *

from base import BaseMethodView
from flask_login import login_user, current_user, login_required, logout_user


bcrypt = None


#Note to self: dont forget to add login or sign up via google / yandex ? 
#I am loosing my damned sanity, seperate the files asap otherwise its gonna be even more painful deal with the 



class MainPageView(BaseMethodView): 
    def get(self):
        stmt = select(User).where(User.is_teacher == True)
        teachers = self.engine.session.execute(stmt).scalars().all()

        if len(teachers) >= 6:
            random_teachers = random.sample(teachers, 6)  #rmeinder to self to change this to not only 6 people later,
        else:
            random_teachers = teachers
            
        user = current_user if current_user.is_authenticated else None

        return render_template('mainpage.html', users= random_teachers, user=user)

    

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
    

class EditSettingView(BaseMethodView):
    def get(self):
        user_id = session.get('user_id')  
        if not user_id:
            return redirect(url_for('signin')) 
        
        form = EditSettingsForm()
        return render_template('settings.html', form=form)
    
    @login_required
    def post(self):
        user_id = session.get('user_id')  #needs to be edited so I can #continue your sentence I have no idea wtf I wrote here forgot
        if not user_id:
            return redirect(url_for('signin'))
   
        form = EditSettingsForm()
        user = self.engine.session.execute(select(User).where(User.id == user_id)).scalar()


        if form.validate_on_submit():
            if form.name.data:
                user.name = form.name.data

            if form.email.data:
                user.email = form.email.data #I dont remember but ig I should've added an email check here
            
            if form.password1.data:
                user.password = bcrypt.generate_password_hash(form.password1.data).decode('utf-8')

            if form.bio.data:
                user.bio = form.bio.data
            
            user.is_teacher = form.is_teacher.data
            
            self.engine.session.commit()

            return redirect(url_for('ind'))
        return render_template('settings.html', form=form)
    

class UserProfileView(BaseMethodView):
    def get(self):
        return render_template('user_profile.html')

    

class UserDashboardView(BaseMethodView):
    @login_required
    def get(self):
        user = current_user

        all_sessions = self.engine.session.execute(select(Sess).where(Sess.teacher_id == current_user.id)).scalars().all()

        for ses in all_sessions:
            if ses.update_status():
                self.engine.session.commit()
        
        pending_requests = self.engine.session.execute(select(SessionRequest)
                                              .join(Sess, SessionRequest.session_id==Sess.id)
                                              .where(Sess.teacher_id==current_user.id, SessionRequest.status=='pending', Sess.start_time > datetime.now())).scalars().all()
        
        for request in pending_requests:
            request.student =  self.engine.session.get(User, request.student_id)
            if request.session:
                request.session.skill = self.engine.session.get(Skill, request.session.skill_id)


        upcoming_sessions = self.engine.session.execute(select(Sess)
                                                        .where(Sess.teacher_id==current_user.id, Sess.status=='booked',
                                                                Sess.end_time > datetime.now()).order_by(Sess.start_time)).scalars().all()

        for s in upcoming_sessions:
            s.skill = self.engine.session.get(Skill, s.skill_id)
            if s.student_id:
                s.student = self.engine.session.get(User, s.student_id)

        recent_reviews = self.engine.session.execute(select(Review)
                                                     .where(Review.teacher_id == current_user.id)
                                                     .order_by(Review.created_at.desc())
                                                     .limit(3)).scalars().all()
        
        for review in recent_reviews:
            review.reviewer = self.engine.session.get(User, review.reviewer_id)



        return render_template('dashboard.html', user = user, 
                                pending_requests=pending_requests,
                                upcoming_sessions=upcoming_sessions,
                                  recent_reviews = recent_reviews
                                  )

    @login_required
    def post(self):
        action = request.form.get('action')
        request_id =  request.form.get('request_id')

        session_request = self.engine.session.execute(select(SessionRequest)
                                                    .where(SessionRequest.id == request_id)).scalar()
        
        ses = self.engine.session.get(Sess, session_request.session_id)

        if ses.teacher_id != current_user.id:
            return redirect(url_for('dashboard'))
        
        if action =='accept':
            ses.status='booked'
            ses.student_id = session_request.student_id
            session_request.status = 'accepted'

            ses.skill = self.engine.session.get(Skill, ses.skill_id)
            skill_name  = ses.skill.name
            teacher_name = current_user.name
            notificaation = Notification(
                user_id = session_request.student_id,
                text =f"Your {skill_name} session request for {teacher_name} was accepted!",
                is_seen = False
            )
            self.engine.session.add(notificaation)
            
        elif action =='decline':
            session_request.status = 'declined'

            ses.skill = self.engine.session.get(Skill, ses.skill_id)
            skill_name  = ses.skill.name
            teacher_name = current_user.name
            notification = Notification(
                user_id = session_request.student_id,
                text =f"Your {skill_name} session request for {teacher_name} was declined!",
                is_seen = False
            )
            self.engine.session.add(notification)
        
        self.engine.session.commit()

        return redirect(url_for('dashboard'))


    

class LogoutView(BaseMethodView):
    def get(self):
        logout_user()
        return redirect(url_for('ind'))
    


#finish this on SUNDAY, plus 
#Do NOT forget to make full CRUD operations on THIS!!!!!
class UserPage(BaseMethodView): # ı need to detail this later still need to think how the html template would look like
    def get(self, user_id):
        posts =  self.engine.session.execute(select(PortfolioPosts).where(PortfolioPosts.user_id == user_id)).scalars().all()
        return render_template('UserPage.html')
    


    @login_required
    def post(self):
        pass



#Do NOT forget to make full CRUD operations on THIS!!!!!
class ReviewView(BaseMethodView): 
    def get(self, teacher_id):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('signup'))
        
        reviews = self.engine.session.execute(select(Review)).scalars().all()
        
        form = ReviewForm()
        return render_template('review.html', form=form, reviews=reviews)
    


    @login_required
    def post(self, teacher_id):
        form = ReviewForm()

        if form.validate_on_submit():
            review = Review(
                comment= form.comment.data,
                reviewer_id = current_user.id,
                teacher_id=teacher_id,
                rating = form.rating.data
            )

            self.engine.session.add(review)
            self.engine.session.commit()
            
            return redirect(url_for('review'))
        
        return render_template('review.html', form = form)
    

    @login_required #make it so users can delete their reviews
    def delete(self, review_id):
        form = ReviewForm()

        if form.validate_on_submit():
            deleted_review = self.engine.session.execute(select(Review).where(Review.id == review_id)).scalar_one_or_none()
            self.engine.session.delete(deleted_review)
            self.engine.session.commit()

        return render_template('review.html', form = form)


    @login_required  #make it so users can edit their reviews
    def patch(self, teacher_id):
        pass




#note to self: finish this damned page toNIHGT I dont wanna see it anymore


#also add the delete ses option on delete,
class MakeSessView(BaseMethodView):
    @login_required
    def get(self):
        user = current_user

        form = MakeSessForm()
        form.skill_id.choices = [(skill.id, skill.name) for skill in user.skills]
        weekly_sessions = self.weekly_schedule(user.id)
        today_date = datetime.now().strftime('%Y-%m-%d')

        return render_template('create_session.html', form=form, weekly_sessions=weekly_sessions, today_date=today_date)
    

    def weekly_schedule(self, teacher_id):
        today = datetime.now().date()
        weekly_data = []
        
        for i in range(7):
            curr_date = today + timedelta(days=i)
            next_date = curr_date + timedelta(days=1)

            sessions = self.engine.session.execute(select(Sess).where(
                Sess.teacher_id == teacher_id,
                Sess.start_time >= curr_date,
                Sess.start_time < next_date
            ).order_by(Sess.start_time)).scalars().all()

            sess_list = []

            for s in sessions:
                skill =  self.engine.session.get(Skill, s.skill_id)
                sess_list.append({
                    'id': s.id,
                    'skill_name': skill.name,
                    'start_time': s.start_time.strftime('%I:%M %p'),
                    'end_time': s.end_time.strftime('%I:%M %p'), 
                    'hourly_rate': s.hourly_rate,
                    'status': s.status
                })


            weekly_data.append({
                'day_name': curr_date.strftime('%A'),
                'date': curr_date.strftime('%b %d'),
                'sessions': sess_list
            })
        
        return weekly_data
    

    @login_required
    def post(self):
        user = current_user

        form = MakeSessForm()
        form.skill_id.choices = [(skill.id, skill.name) for skill in user.skills]

        if form.validate_on_submit():

            date_str = form.start_date.data
            start_time_str = form.start_time.data
            end_time_str = form.end_time.data
            recurring = form.recurring.data
            week_count = form.weeks_count.data if recurring else 1

            start_time =  datetime.strptime(f"{date_str} {start_time_str}", '%Y-%m-%d %H:%M')
            end_time =  datetime.strptime(f"{date_str} {end_time_str}", '%Y-%m-%d %H:%M')

            if end_time < start_time:
                flash('The end time must BE after the start time', 'error')
                return redirect(url_for('make_session'))
            
            if start_time.date() <= datetime.now().date():
                flash('You cant create a session in the past :)', 'error')
                return redirect(url_for('make_session'))
            

            lesson_length = (end_time - start_time).total_seconds() / 60

            if lesson_length < 30:
                flash('Lesson duration should be longer than 30 minutes.')
                return redirect(url_for('make_session'))
            
            if lesson_length > 180:
                flash('Lesson duration should be shorter than 180 minutes.')
                return redirect(url_for('make_session'))


            created_sessions = []

            for week in range(week_count):
                lesson_start = start_time + timedelta(weeks=week)
                lesson_end = end_time + timedelta(weeks=week)

                if lesson_start.date() < datetime.now().date():
                    continue

                overlapped_lessons = self.engine.session.execute(
                    select(Sess).where(
                        Sess.teacher_id == user.id,
                        Sess.status == 'booked',
                        Sess.start_time < lesson_end,
                        Sess.end_time > lesson_start
                    )
                ).scalars().all()

                if overlapped_lessons:
                    flash(f"Week {week+1}: Session on {lesson_start.strftime("%b %d")}conflicts with existing booked session", "warning")
                    continue

                sess = Sess(
                    teacher_id= current_user.id,
                    skill_id = form.skill_id.data,
                    start_time= lesson_start,
                    end_time= lesson_end,
                    hourly_rate = form.hourly_rate.data
                )
                self.engine.session.add(sess)
                created_sessions.append(sess)

            if user.is_teacher != True:
                user.is_teacher = True
            
            self.engine.session.commit()

            if len(created_sessions) == 1:
                flash('Session was created without an issue.')
            elif len(created_sessions) > 1:
                flash('All sessions are created without an issue.')
            else:
                flash('No session was created')

            return redirect(url_for('make_session'))
        

        weekly_sessions = self.weekly_schedule(user.id)
        today_date = datetime.now().strftime('%Y-%m-%d')
        return render_template('create_session.html', form=form, weekly_sessions=weekly_sessions, today_date=today_date)
    

class DeleteSessionView(BaseMethodView):

    @login_required
    def delete(self, session_id):
        ses = self.engine.session.execute(select(Sess).where(Sess.id == session_id)).scalar_one_or_none()

        if not ses:
            return {'error': 'Session not found'}, 404
        
        if ses.status == 'booked':
            return {'error': 'Cannot delete a booked session, please let the student know beforehand'}, 400
            
        self.engine.session.execute(delete(SessionRequest).where(SessionRequest.session_id == session_id))

        self.engine.session.delete(ses)
        self.engine.session.commit()


        return {'message': 'Session is deleted'}, 200

    

#need to learn websockets for this thing

class UserMessageView(BaseMethodView):
    pass