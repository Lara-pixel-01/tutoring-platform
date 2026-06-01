from flask import jsonify
from flask_login import current_user
from sqlalchemy import select, update, func
from base import BaseResource
from models import Notification


class NotificationApi(BaseResource):
    def get(self):
        if not current_user.is_authenticated:
            return {'error': 'Unauthorized'}, 401
        

        notifications = self.engine.session.execute(
            select(Notification).where(Notification.user_id == current_user.id)
            .order_by(Notification.created_at.desc())
        ).scalars().all()
        
        unread_count = sum(1 for n in notifications if not n.is_seen)
        
        return {
            'notifications': [{
                'id': n.id,
                'text': n.text,
                'time': n.created_at.strftime('%H:%M %d.%m'),
                'is_read': n.is_seen
            } for n in notifications],
            'unread_count': unread_count
        }
    
    def post(self):
        if not current_user.is_authenticated:
            return {'error': 'Unauthorized'}, 401
        
        self.engine.session.execute(
            update(Notification).where(Notification.user_id == current_user.id)
            .values(is_seen=True)
        )
        self.engine.session.commit()
        return {'success': True}


class UnreadCountApi(BaseResource):
    def get(self):
        if not current_user.is_authenticated:
            return {'count': 0}
        
        count = self.engine.session.execute(
            select(func.count()).select_from(Notification)
            .where(Notification.user_id == current_user.id, Notification.is_seen == False)
        ).scalar() or 0
        
        return {'count': count}