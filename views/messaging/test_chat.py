import pytest
from flask_bcrypt import Bcrypt
    

def test_chat_page_loads_authenticated(client, test_user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
    
    response = client.get('/chat/')
    assert response.status_code == 200
    assert b'Chat' in response.data or b'chat' in response.data.lower()


def test_chat_with_user_loads(client, test_user, db_session):
    from models import User
    
    bcrypt = Bcrypt()
    
    other_user = User(
        email='other@test.com',
        password=bcrypt.generate_password_hash('pass').decode('utf-8'),
        name='Other User',
        is_teacher=False
    )
    db_session.add(other_user)
    db_session.commit()
    
    
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
    
    response = client.get(f'/chat/{other_user.id}')
    assert response.status_code == 200
    assert b'Other User' in response.data


def test_message_saved_to_database(client, test_user, db_session):
    from models import User, Message

    
    bcrypt = Bcrypt()

    other_user = User(
        email='msg_test@test.com',
        password=bcrypt.generate_password_hash('pass').decode('utf-8'),
        name='Message User',
        is_teacher=False
    )
    db_session.add(other_user)
    db_session.commit()
    
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)

    new_message = Message(
        sender_id=test_user.id,
        receiver_id=other_user.id,
        text='Test message content',
        is_read=False
    )


    db_session.add(new_message)
    db_session.commit()
    saved = db_session.get(Message, new_message.id)
    assert saved is not None
    assert saved.text == 'Test message content'
    assert saved.sender_id == test_user.id
    assert saved.receiver_id == other_user.id