from base import BaseResource
from models import User
from sqlalchemy import select

class UserProfileApi(BaseResource):
    def get(self, user_id: int):
        user = self.engine.session.execute(select(User).where(User.id == user_id)).scalar()

        if not user:
            return {'error': 'No such user'}, 404
        
        return  {
            'id': user.id,
            'name': user.name,
            'bio': user.bio,
            'is_teacher': user.is_teacher,
            'profile_pic': user.profile_pic,
            'skills': [{'id': s.id, 'name': s.name, 'category':s.category} for s in user.skills],
        }