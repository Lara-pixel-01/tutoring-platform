from datetime import datetime, timedelta, timezone
from flask import render_template, url_for, redirect, flash, request
from sqlalchemy import select, delete


from models import Skill, SessionRequest, Sess

from forms import *

from base import BaseMethodView
from flask_login import current_user, login_required

from utils.timezone_utils import localize_datetime, get_user_timezone


#I completely forget for skills the hourly rate must be same, later modify it Currently not modified.


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
        today = datetime.now(timezone.utc).date()
        weekly_data = []
        user_tz = get_user_timezone()
        
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

                local_start = localize_datetime(s.start_time, user_tz)
                local_end = localize_datetime(s.end_time, user_tz)

                sess_list.append({
                    'id': s.id,
                    'skill_name': skill.name,
                    'start_time': local_start.strftime('%I:%M %p'),
                    'end_time': local_end.strftime('%I:%M %p'), 
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
                        Sess.status.in_(['booked','free']),
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
    

class TeacherSessionsView(BaseMethodView):
    def get(self, user_id, skill_id=None):
        teacher = self.engine.session.get(User, user_id)
        if not teacher or not teacher.is_teacher:
            flash('Teacher not found', 'error')
            return redirect(url_for('ind'))
        
        skill_id = request.args.get('skill_id', type=int)
        
        now = datetime.now()
        
        stmt = select(Sess).where(
            Sess.teacher_id == user_id,
            Sess.status == 'free',
            Sess.start_time > now
        )
        
        if skill_id:
            stmt = stmt.where(Sess.skill_id == skill_id)
            selected_skill = self.engine.session.get(Skill, skill_id)
        else:
            selected_skill = None
        
        stmt = stmt.order_by(Sess.start_time)
        sessions = self.engine.session.execute(stmt).scalars().all()

        user_tz = get_user_timezone()
        
        for session in sessions:
            session.skill = self.engine.session.get(Skill, session.skill_id)
            session.local_start_time = localize_datetime(session.start_time, user_tz)
        
        form = SessionRequestForm()
        
        return render_template('teacher_sessions.html',
                              teacher=teacher,
                              sessions=sessions,
                              selected_skill=selected_skill,
                              form=form)
    
    @login_required
    def post(self, user_id):
        form = SessionRequestForm()
        
        if form.validate_on_submit():
            session_id = request.form.get('session_id')
            student_level = form.student_level.data
            student_goals = form.student_goals.data
            
            if not session_id:
                flash('Please select a session first', 'error')
                return redirect(url_for('teacher_sessions', user_id=user_id))
            
            session = self.engine.session.get(Sess, session_id)
            if not session or session.status != 'free':
                flash('Session not available', 'error')
                return redirect(url_for('teacher_sessions', user_id=user_id))
            
    
            existing = self.engine.session.execute(select(SessionRequest).where(
                SessionRequest.session_id == session_id,
                SessionRequest.student_id == current_user.id
            )).scalar_one_or_none()
            
            if existing:
                flash('You already requested this session', 'warning')
                return redirect(url_for('teacher_sessions', user_id=user_id))
            
            session_request = SessionRequest(
                session_id=session_id,
                student_id=current_user.id,
                student_level=student_level,
                student_goals=student_goals,
                status='pending'
            )
            self.engine.session.add(session_request)
            self.engine.session.commit()
            
            flash('Session request sent to teacher!', 'success')
            return redirect(url_for('dashboard'))
        
        return redirect(url_for('teacher_sessions', user_id=user_id))