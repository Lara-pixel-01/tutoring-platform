from base import BaseResource
from models import Sess, Skill, User
from sqlalchemy import select
from flask_login import login_required, current_user


class MyLessonsApi(BaseResource):
    @login_required
    def get(self):

        user = current_user

        res = []


        if user.is_teacher:

            teaching_ses = self.engine.session.execute(
                select(Sess).where(Sess.teacher_id==user.id).order_by(Sess.start_time)
            ).scalars().all()

            for ses in teaching_ses:
                skill = self.engine.session.execute(
                     select(Skill).where(Skill.id == ses.skill_id)
                ).scalar_one_or_none()

                student_name =  None

                if ses.student_id:
                    student = self.engine.session.get(User, ses.student_id)
                    student_name = student.name if student else None

                res.append({
                    'role': 'teacher',
                    'id': ses.id,
                    'skill': skill.name,
                    'start_time': ses.start_time.isoformat(),
                    'hourly_rate': ses.hourly_rate,
                    'status': ses.status,
                    'student_name': student_name
                })
        
        learning = self.engine.session.execute(
                select(Sess).where(Sess.student_id==user.id).order_by(Sess.start_time)
        ).scalars().all()

        for ses in learning:
                skill = self.engine.session.get(Skill, ses.skill_id)
                teacher = self.engine.session.get(User, ses.teacher_id)

                res.append({
                    'role': 'student',
                    'id': ses.id,
                    'skill': skill.name,
                    'start_time': ses.start_time.isoformat(),
                    'end_time': ses.end_time.isoformat(),
                    'hourly_rate': ses.hourly_rate,
                    'status': ses.status,
                    'teacher_name': teacher.name
                })

        res.sort(key=lambda x: x['start_time'])

        return {
            'sessions': res,
            'as_teacher': user.is_teacher
        }