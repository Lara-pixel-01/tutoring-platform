import pytest
from datetime import datetime, timedelta
from sqlalchemy import select
from flask_bcrypt import Bcrypt
from flask.testing import FlaskClient
from models import Sess, SessionRequest, Skill, User

def test_dashboard_unauthenticated_user(client: FlaskClient):

    res = client.get('/dashboard/', follow_redirects=True)
    assert b'Find a teacher' in res.data or b'find' in res.data.lower()




def test_accept_request_updates_session_status(client: FlaskClient, test_user: User, db_session):
    
    tomorrow = datetime.now() + timedelta(days=1)
    skill = db_session.query(Skill).first()

    session = Sess(
        teacher_id=test_user.id,
        skill_id=skill.id,
        start_time=tomorrow,
        end_time=tomorrow + timedelta(hours=1),
        hourly_rate=50,
        status='free'
    )



    db_session.add(session)
    db_session.commit()

    bcrypt = Bcrypt()
    student = User(
        email='sdfdfdfd@test.com',
        password=bcrypt.generate_password_hash('pass').decode('utf-8'),
        name='bob2',
        is_teacher=False
    )
    db_session.add(student)
    db_session.commit()

    session_request = SessionRequest(
        session_id=session.id,
        student_id=student.id,
        student_level='Beginner',
        status='pending'
    )
    db_session.add(session_request)
    db_session.commit()
    
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
    
    response = client.post('/dashboard/', data={
        'action': 'accept',
        'request_id': session_request.id
    }, follow_redirects=True)
    
    assert response.status_code == 200

    updated_session = db_session.get(Sess, session.id)
    assert updated_session.status == 'booked'
    assert updated_session.student_id == student.id


def test_decline_request_removes_from_pending(client: FlaskClient, test_user: User, db_session):
    from models import Sess, SessionRequest, Skill, User

    tomorrow = datetime.now() + timedelta(days=1)
    skill = db_session.query(Skill).first()
    
    session = Sess(
        teacher_id=test_user.id,
        skill_id=skill.id,
        start_time=tomorrow,
        end_time=tomorrow + timedelta(hours=1),
        hourly_rate=50,
        status='free'
    )
    db_session.add(session)
    db_session.commit()
    
    bcrypt = Bcrypt()
    student = User(
        email='decline@test.com',
        password=bcrypt.generate_password_hash('pass').decode('utf-8'),
        name='Decline Student',
        is_teacher=False
    )
    db_session.add(student)
    db_session.commit()
    
    session_request = SessionRequest(
        session_id=session.id,
        student_id=student.id,
        student_level='Beginner',
        status='pending'
    )


    
    db_session.add(session_request)
    db_session.commit()
    
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
    
    response = client.post('/dashboard/', data={
        'action': 'decline',
        'request_id': session_request.id
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    updated_request = db_session.get(SessionRequest, session_request.id)
    assert updated_request.status == 'declined'



def test_student_dashboard_upcoming_sessions(client, test_user, db_session):
    from models import Sess, Skill, User
    from flask_bcrypt import Bcrypt
    
    bcrypt = Bcrypt()
    
    student = User(
        email='student@test.com',
        password=bcrypt.generate_password_hash('pass').decode('utf-8'),
        name='Test Student',
        is_teacher=False
    )
    db_session.add(student)
    db_session.commit()
    
    tomorrow = datetime.now() + timedelta(days=1)
    skill = db_session.query(Skill).first()
    
    session = Sess(
        teacher_id=test_user.id,
        student_id=student.id,
        skill_id=skill.id,
        start_time=tomorrow,
        end_time=tomorrow + timedelta(hours=1),
        hourly_rate=50,
        status='booked'
    )
    db_session.add(session)
    db_session.commit()

    with client.session_transaction() as sess:
        sess['_user_id'] = str(student.id)
    
    response = client.get('/student-dashboard')
    assert response.status_code == 200
    assert b'Upcoming' in response.data or b'upcoming' in response.data.lower()