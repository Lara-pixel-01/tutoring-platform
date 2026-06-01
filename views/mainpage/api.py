from base import BaseResource
from models import User, Review, Sess
from sqlalchemy import select, func


class SortTeacherApi(BaseResource):
    def get(self):
        teachers = self.engine.session.execute(select(User).where(User.is_teacher==True)).scalars().all()

        for teacher in teachers:
            avg_rating = self.engine.session.execute(select(func.avg(Review.rating))
                                                    .where())
            
            data = []

            for teacher in teachers:

                avg_rating = self.engine.session.execute(
                    select(func.avg(Review.rating)).where(Review.teacher_id == teacher.id)).scalar()
                
                data.append({
                    'id': teacher.id,
                    'name': teacher.name,
                    'bio': teacher.bio,
                    'skills': [s.name for s in teacher.skills],
                    'avg_rating': round(float(avg_rating), 2),
                    'review_count': len(teacher.reviews_received)
                })

            def get_rating(teacher):
                return teacher['avg_rating']
            
            data.sort(key=get_rating, reverse=True)

            return {'teachers': data, 'count': len(data), 'sort_by': 'rating'}
                


class SortByPriceDescAPI(BaseResource):
    def get(self):

        teachers = self.engine.session.execute(select(User).where(User.is_teacher==True)).scalars().all()

        data = []

        for teacher in teachers:
            min_price = self.engine.session.execute(
                select(func.min(Sess.hourly_rate)).where(Sess.teacher_id==teacher.id)).scalar() 

            data.append({
                'id': teacher.id, 
                'name': teacher.name,
                'bio': teacher.bio,
                'skills': [s.name for s in teacher.skills],
                'min_price': round( float(min_price), 2)
            })

        def get_price(teacher):
            return teacher['min_price']
        
        data.sort(key=get_price, reverse=True)
    
        return {'teachers': data, 'sort_by': 'min_price'}
    

class SortByPriceAscAPI(BaseResource):
    def get(self):
        
        
        teachers = self.engine.session.execute(select(User).where(User.is_teacher==True)).scalars().all()

        data = []

        for teacher in teachers:
            min_price = self.engine.session.execute(
                select(func.min(Sess.hourly_rate)).where(Sess.teacher_id==teacher.id)).scalar() 

            data.append({
                'id': teacher.id, 
                'name': teacher.name,
                'bio': teacher.bio,
                'skills': [s.name for s in teacher.skills],
                'min_price': round( float(min_price), 2)
            })

        def get_price(teacher):
            return teacher['min_price']
        
        data.sort(key=get_price)
    
        return {'teachers': data, 'sort_by': 'min_price'}
    