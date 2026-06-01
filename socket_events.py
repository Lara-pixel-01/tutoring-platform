from extenstions import socketio, db
from flask_login import current_user
from flask_socketio import emit, join_room
from models import Message, Notification
from datetime import datetime


@socketio.on('connect')
def handle_connect() -> None:
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        join_room(f'notifications_{current_user.id}')
        print(f'User {current_user.name} connected')


@socketio.on('disconnect')
def handle_disconnect() -> None:
    if current_user.is_authenticated:
        print(f'User {current_user.name} disconnected')


@socketio.on('private_message')
def handle_private_message(data: dict) ->None:
    if not current_user.is_authenticated:
        return
    
    recipient_id = data.get('recipient_id')
    message_text = data.get('message', '').strip()

    if not message_text:
        return
    
    new_message = Message(
        sender_id = current_user.id,
        receiver_id = recipient_id,
        text = message_text,
        is_read =  False
    )

    db.session.add(new_message)
    db.session.commit()

    emit('new_message', {
        'sender_id': current_user.id,
        'sender_name': current_user.name,
        'message': message_text,
        'timestamp': new_message.created_at.strftime('%H:%M')
    }, room=f'user_{recipient_id}')


def send_notifications(user_id: int, title: str, message:str) -> None:
    socketio.emit('new_notification', {
        'title': title,
        'message': message,
        'timestamp': datetime.now().strftime('%H:%M')
    },  room=f'notifications_{user_id}')


def save_and_send_notification(user_id: int, title: str, message:str) -> None:
    
    notif = Notification(
        user_id = user_id,
        text=f"{title}: {message}",
        is_seen = False
    )

    db.session.add(notif)
    db.session.commit()

    send_notifications(user_id, title,message)