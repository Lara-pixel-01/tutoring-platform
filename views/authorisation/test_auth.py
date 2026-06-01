import pytest

from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()

def test_duplicate_emails(client, db_session):
    from models import User
     
    user1 = User(
        email = 'somedup12@gmail.com',
        password = bcrypt.generate_password_hash('pass23').decode('utf-8'),
        name='Some Name',
    )
    db_session.add(user1)
    db_session.commit()

    res = client.post('/signup/', data= {
        'name': 'another Name',
        'email': 'somedup12@gmail.com',
        'password1': 'pass23',
        'password2': 'pass23',
        'submit': 'signup'
    })

    assert res.status_code == 200


def test_wrong_password(client, db_session): 
    from models import User

    user = User(
        email = 'idk@mail.com',
        password = bcrypt.generate_password_hash('sadasdsdf').decode('utf-8'),
        name='knefzxr',
    )

    db_session.add(user)
    db_session.commit()

    res = client.post('/signin/', data= {
        'email': 'idk@mail.com',
        'password': 'kefnsdkfnskfdnkdfn',
        'submit': 'sign in'
    }, 
    follow_redirects = True)

    assert b'Sign In' in res.data or b'sign in' in res.data.lower()


def test_signup_adds_user(client, db_session):

    res = client.post('/signup/', data={
        'name':'bob',
        'email': 'bob12@mail.com',
        'password1': 'bob123',
        'password2': 'bob123',
        'submit': 'signup'
    }, follow_redirects = True)

    from models import User
    from sqlalchemy import select
    user = db_session.execute(select(User).where(User.email == 'bob12@mail.com')).scalar_one_or_none()

    assert user is not None
    assert user.name == 'bob'
    assert user.email == 'bob12@mail.com'