import pytest


def test_notification_returns_json(client, test_user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
    
    response = client.get('/api/notifications')
    assert response.status_code == 200
    assert response.is_json


def test_notification_unread_count(client, test_user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
    
    response = client.get('/api/notifications/unread-count')
    assert response.status_code == 200
    assert response.is_json
    assert 'count' in response.json


def test_mark_notifications_read(client, test_user, db_session):
    from models import Notification
    
    notif = Notification(
        user_id=test_user.id,
        text='Testing notifs',
        is_seen=False
    )
    db_session.add(notif)
    db_session.commit()
    
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
    
    response = client.post('/api/notifications')
    assert response.status_code == 200
    
    updated = db_session.get(Notification, notif.id)
    assert updated.is_seen is True