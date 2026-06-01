import pytest
from flask_bcrypt import Bcrypt
from sqlalchemy import select
from flask.testing import FlaskClient
from models import User, Review

from sqlalchemy.orm.scoping import scoped_session

bcrypt = Bcrypt()


'''tHS basically checks if the review page loads properly or nah'''

def test_review_page_loads(client: FlaskClient, test_user: User) -> None:

    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
    
    response = client.get(f'/review/{test_user.id}')
    assert response.status_code == 200
    assert b'Reviews' in response.data or b'review' in response.data.lower()



''' preeety self explanatory it checks if the creating review works properly or nah, same for delete, and edit'''

def test_user_can_create_review(client: FlaskClient, test_user: User, db_session: scoped_session) -> None:
    
    student = User(
        email='sdasdasdasdw@test.com',
        password=bcrypt.generate_password_hash('pass').decode('utf-8'),
        name='bob3',
        is_teacher=False
    )
    db_session.add(student)
    db_session.commit()
    
    with client:
        client.post('/signin/', data={
            'email': 'sdasdasdasdw@test.com',
            'password': 'pass',
            'submit': 'sign in'
        })
        
        response = client.post(f'/review/{test_user.id}', data={
            'rating': 5,
            'comment': 'Amazing teacher, wo hoo',
            'submit': 'Send'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        stmt = select(Review).where(
            Review.reviewer_id == student.id,
            Review.teacher_id == test_user.id
        )
        saved = db_session.execute(stmt).scalar_one_or_none()
        
        assert saved is not None
        assert saved.rating == 5
        assert saved.comment == 'Amazing teacher, wo hoo'


def test_user_can_edit_own_review(client: FlaskClient, test_user: User, db_session: scoped_session) -> None: 
    student = User(
        email='somethng45@test.com',
        password=bcrypt.generate_password_hash('pass').decode('utf-8'),
        name='Edit Student',
        is_teacher=False
    )
    db_session.add(student)
    db_session.commit()
    
    review = Review(
        comment='smth',
        reviewer_id=student.id,
        teacher_id=test_user.id,
        rating=4
    )
    db_session.add(review)
    db_session.commit()
    review_id = review.id
    
    with client:
        client.post('/signin/', data={
            'email': 'somethng45@test.com',
            'password': 'pass',
            'submit': 'sign in'
        })
        
        response = client.post(f'/review/update/{review_id}', data={
            'rating': 5,
            'comment': 'Updated comment'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        updated = db_session.get(Review, review_id)
        assert updated.comment == 'Updated comment'
        assert updated.rating == 5



def test_user_can_delete_own_review(client: FlaskClient, test_user: User, db_session: scoped_session) -> None:
    student = User(
        email='sfdfdfdfdfdfd@test.com',
        password=bcrypt.generate_password_hash('pass').decode('utf-8'),
        name='ddfdfdfdfd',
        is_teacher=False
    )
    db_session.add(student)
    db_session.commit()
    
    review = Review(
        comment='This will be deleted',
        reviewer_id=student.id,
        teacher_id=test_user.id,
        rating=3
    )
    db_session.add(review)
    db_session.commit()
    review_id = review.id
    
    with client:
        client.post('/signin/', data={
            'email': 'sfdfdfdfdfdfd@test.com',
            'password': 'pass',
            'submit': 'sign in'
        })
        
        response = client.post(f'/review/delete/{review_id}', follow_redirects=True)
        assert response.status_code == 200
        
        deleted = db_session.get(Review, review_id)
        assert deleted is None