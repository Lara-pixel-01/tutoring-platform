from datetime import datetime
from flask import render_template, request, url_for, redirect
from sqlalchemy import select

from models import User, Skill, SessionRequest, Sess, Notification, Review

from forms import *

from base import BaseMethodView
from flask_login import current_user, login_required
from utils.timezone_utils import localize_datetime, get_user_timezone


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


        user_tz = get_user_timezone()

        upcoming_sessions = self.engine.session.execute(select(Sess)
                                                        .where(Sess.teacher_id==current_user.id, Sess.status=='booked',
                                                                Sess.end_time > datetime.now()).order_by(Sess.start_time)).scalars().all()

        for s in upcoming_sessions:
            s.skill = self.engine.session.get(Skill, s.skill_id)
            if s.student_id:
                s.student = self.engine.session.get(User, s.student_id)
            s.local_start_time = localize_datetime(s.start_time, user_tz)

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
    


class StudentDashboardView(BaseMethodView):
    @login_required
    def get(self):
        user = current_user

        user_tz = get_user_timezone()
        
        upcoming = self.engine.session.execute(
            select(Sess).where(
                Sess.student_id == user.id,
                Sess.status == 'booked',
                Sess.start_time > datetime.now()
            ).order_by(Sess.start_time)
        ).scalars().all()

        
        for s in upcoming:
            s.skill = self.engine.session.get(Skill, s.skill_id)
            s.teacher = self.engine.session.get(User, s.teacher_id)
            s.local_start_time = localize_datetime(s.start_time, user_tz)  
        
        
        pending = self.engine.session.execute(
            select(SessionRequest).where(
                SessionRequest.student_id == user.id,
                SessionRequest.status == 'pending'
            )
        ).scalars().all()
        
        for req in pending:
            if req.session:
                req.session.skill = self.engine.session.get(Skill, req.session.skill_id)
                req.session.teacher = self.engine.session.get(User, req.session.teacher_id)
        
        for s in upcoming:
            s.skill = self.engine.session.get(Skill, s.skill_id)
            s.teacher = self.engine.session.get(User, s.teacher_id)
        
        return render_template('student_dashboard.html',user=user,upcoming=upcoming, pending=pending)