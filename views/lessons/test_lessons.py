import pytest

from flask_bcrypt import Bcrypt

from datetime import datetime, timedelta


bcrypt = Bcrypt()



def test_lesson_duration(client, test_user):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)

    res = client.post('/create-session', data= {
        'skill_id': test_user.skills[0].id,
        'start_date': tomorrow,
        'start_time': '10:30',
        'end_time': '15:30',
        'hourly_rate': '34',
        'recurring': False,
        'weeks_count': 1,
        'submit': 'Create Session'
    }, follow_redirects= True)

    assert b'180' in res.data 


def test_overlapping_lessons(client, test_user):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)

        res1 = client.post('/create-session', data = {
            'skill_id': test_user.skills[0].id,
            'start_date': tomorrow,
            'start_time': '10:30',
            'end_time': '11:30',
            'hourly_rate': '34',
            'recurring': False,
            'weeks_count': 1,
            'submit': 'Create Session'
        }, follow_redirects= True)

        res2 = client.post('/create-session', data = {
            'skill_id': test_user.skills[0].id,
            'start_date': tomorrow,
            'start_time': '10:30',
            'end_time': '11:30',
            'hourly_rate': '34',
            'recurring': False,
            'weeks_count': 1,
            'submit': 'Create Session'
        }, follow_redirects= True)

        assert b'overlap' in res2.data.lower() or b'conflict' in res2.data.lower()


def test_create_delete_lesson(client, test_user, db_session):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)

    
    res = client.post('/create-session', data = {
            'skill_id': test_user.skills[0].id,
            'start_date': tomorrow,
            'start_time': '10:30',
            'end_time': '11:30',
            'hourly_rate': '34',
            'recurring': False,
            'weeks_count': 1,
            'submit': 'Create Session'
        }, follow_redirects= True)
    
    assert b'created' in res.data.lower()

    from models import Sess
    from sqlalchemy import select

    ses = db_session.execute(select(Sess).where(
        Sess.teacher_id == test_user.id,
        Sess.start_time == datetime.strptime(f"{tomorrow} 10:30", '%Y-%m-%d %H:%M')
    )).scalar_one_or_none()

    assert ses is not None

    delete_res = client.delete(f'/delete-session/{ses.id}')
    assert delete_res.status_code == 200


def test_timezone_conversion():
    from utils.timezone_utils import localize_datetime
    utc_time = datetime(2026, 5, 28, 10, 0, 0)
    
    local_ny = localize_datetime(utc_time, 'America/New_York')
    assert local_ny.hour == 6
    
    local_tokyo = localize_datetime(utc_time, 'Asia/Tokyo')
    assert local_tokyo.hour == 19
    
    local_london = localize_datetime(utc_time, 'Europe/London')
    assert local_london.hour == 11


def test_timezone_conversion_winter():
    from utils.timezone_utils import localize_datetime
    utc_time_winter = datetime(2026, 12, 28, 10, 0, 0)
    
    local_ny = localize_datetime(utc_time_winter, 'America/New_York')
    assert local_ny.hour == 5
    
    local_london = localize_datetime(utc_time_winter, 'Europe/London')
    assert local_london.hour == 10