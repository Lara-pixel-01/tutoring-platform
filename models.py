import random
from typing import List, Optional as OptionalTip
from faker import Faker
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from sqlalchemy import ForeignKey, select, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func 

from extenstions import db

fake = Faker()

#to add:

#possibly tags table

#DATABASE TABLES =============================================================================================

user_skills = db.Table('user_skills',
                      db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                      db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True)

)




class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    email: Mapped[str] = mapped_column(db.String(100), unique=True)
    password: Mapped[str] = mapped_column(db.String(100))
    name: Mapped[str] = mapped_column(db.String(100))
    bio: Mapped[OptionalTip[str]] = mapped_column(db.String(999))
    profile_pic: Mapped[OptionalTip[str]] = mapped_column(db.String(999))
    is_teacher: Mapped[bool] = mapped_column(db.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    #seperation purposes, below are the relationships:

    skills: Mapped[List["Skill"]] = relationship(secondary=user_skills, back_populates='users')

    reviews_written: Mapped[List["Review"]] = relationship(foreign_keys="Review.reviewer_id", back_populates="reviewer",  cascade="all, delete-orphan")
    reviews_received: Mapped[List["Review"]] = relationship(foreign_keys="Review.teacher_id", back_populates="teacher", cascade="all, delete-orphan")

    portfolio: Mapped[List["PortfolioPosts"]] = relationship(back_populates='user', cascade="all, delete-orphan")

    sent_messages: Mapped[List["Message"]] = relationship(foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_messages: Mapped[List["Message"]] = relationship(foreign_keys="Message.receiver_id", back_populates="receiver", cascade="all, delete-orphan")

    notifications: Mapped[List["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    settings: Mapped['UserSettings'] = relationship(back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)




class Skill(db.Model, UserMixin):
    __tablename__ = 'skills'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100))
    category: Mapped[str] = mapped_column(db.String(100))
    
    #seperation purposes, below are the relationships:
    users: Mapped[List['User']] = relationship(secondary=user_skills, back_populates='skills')




class SessionRequest(UserMixin, db.Model):
    __tablename__ = 'session_requests'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey('sessions.id'))
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    student_level: Mapped[str] = mapped_column(db.String(100)) # later could make this selectable, like beginner, intermidiate and professional etc
    student_goals: Mapped[OptionalTip[str]] = mapped_column(db.String(1999))
    status: Mapped[str] =  mapped_column(db.String(200), default='pending')

    #seperation purposes, below are the relationships:
    session: Mapped["Sess"] = relationship(back_populates='session_requests')




class Sess(db.Model, UserMixin):
    __tablename__ = 'sessions'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    student_id: Mapped[OptionalTip[int]] = mapped_column(ForeignKey('users.id')) #note to self, this can be null when not booked
    skill_id: Mapped[int] = mapped_column(ForeignKey('skills.id'))
    start_time: Mapped[datetime] =  mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    #is_booked: Mapped[bool] = mapped_column(db.Boolean, default=False) maybe not needed since we have student şd and stattus
    hourly_rate: Mapped[float] = mapped_column(db.Float)
    status: Mapped[str] =  mapped_column(db.String(200), default='free') #make these statusses like free, pending, booked, finished
    meeting_link: Mapped[OptionalTip[str]] = mapped_column(db.String(999)) #will only appear after the status is booked

    #seperation purposes, below are the relationships:
    session_requests: Mapped[List["SessionRequest"]] = relationship(back_populates='session')

    def update_status(self):
        now = datetime.now()

        if self.status == 'free' and self.start_time < now:
            self.status = 'expired'
            return True
        elif self.status == 'booked' and self.end_time < now:
            self.status = 'finished'
            return True
        return False





class Review(db.Model, UserMixin):
    __tablename__ = 'reviews'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    comment: Mapped[str] = mapped_column(db.String(9999))
    reviewer_id: Mapped[int] = mapped_column(ForeignKey('users.id')) #whos the user taht is making the comment
    teacher_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    rating: Mapped[int] = mapped_column(db.Integer) #maybe from 1 to 5 stars? idek will think latr
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    #seperation purposes, below are the relationships:

    reviewer: Mapped["User"] = relationship(foreign_keys=[reviewer_id], back_populates="reviews_written")
    teacher: Mapped["User"] = relationship(foreign_keys=[teacher_id], back_populates="reviews_received")



class PortfolioPosts(db.Model, UserMixin):
    __tablename__ = "portfolio_posts"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    text: Mapped[OptionalTip[str]] =  mapped_column(db.String(2000))
    image: Mapped[str] =  mapped_column(db.String(255)) # note to self to remember store it as a reference
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    #seperation purposes, below are the relationships:

    user: Mapped["User"] = relationship(back_populates="portfolio")



class Message(db.Model, UserMixin):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey('users.id')) #whos the user taht is making the comment
    receiver_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    text: Mapped[OptionalTip[str]] =  mapped_column(db.String(9999))
    is_read: Mapped[bool] = mapped_column(db.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sender: Mapped["User"] = relationship(foreign_keys=[sender_id], back_populates="sent_messages")
    receiver: Mapped["User"] = relationship(foreign_keys=[receiver_id], back_populates="received_messages")

    #Im TIREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEED



class Notification(db.Model, UserMixin):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    text: Mapped[str] =  mapped_column(db.String(999))
    is_seen: Mapped[bool] = mapped_column(db.Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="notifications")

#I just realised I dont have one to one relationshio so added ths

class UserSettings(db.Model, UserMixin):
    __tablename__ = "user_settings"
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    timezone: Mapped[OptionalTip[str]] = mapped_column(db.String(50), default='UTC')

    user: Mapped['User'] = relationship(back_populates='settings')



def create_db(app:Flask):
    with app.app_context(): 
        db.create_all()


def fill_db(app: Flask):  
    from flask_bcrypt import Bcrypt

    bcrypt = Bcrypt()

    with app.app_context():   
        db.drop_all()
        db.create_all()


        skill_cat = {
            "Programming": ['Python', 'Java', "SQL"],
            "Language": ['English', 'Japanese', 'Chinese'],
            "Maths": ['Algebra', 'Calculus', 'Statistics','Probability']
        }
        
        for category, skill in skill_cat.items():
            for name in skill:
                user_skill = Skill(
                    name=name,
                    category=category
                )
                db.session.add(user_skill)
        db.session.commit()


            
        for i in range(20):
            user = User(email= fake.email(),
                password = bcrypt.generate_password_hash(fake.password()).decode('utf-8'),
                name = fake.name(),
                bio = fake.paragraph(nb_sentences=random.randint(3, 7)),
                is_teacher = fake.boolean()
            )

            db.session.add(user)
        db.session.commit()

        teachers = db.session.execute(select(User).where(User.is_teacher==True)).scalars().all()

        skills = db.session.execute(select(Skill)).scalars().all()

        for teacher in teachers:
            skill_count =  random.randint(1,3)
            teacher_skill = random.sample(skills, skill_count)
            teacher.skills.extend(teacher_skill)
        
        db.session.commit()



        for teacher in teachers:
            users  =  db.session.execute(select(User).where(User.id != teacher.id)).scalars().all()
            review_count = random.randint(3,10)

            reviewers = random.sample(users, min(review_count, len(users)))

            for reviewer in reviewers:
                review = Review(
                    comment = fake.paragraph(nb_sentences=random.randint(1,3)),
                    reviewer_id = reviewer.id,
                    teacher_id = teacher.id,
                    rating = random.choice([3.5, 3, 4, 5, 4.5])
                )
                db.session.add(review)

        for teacher in teachers:

            for x in range(random.randint(3,6)):
                start = fake.date_time_between(start_date='-30d', end_date='+30d')
                end = start + timedelta(hours=1)

                sess = Sess(
                    teacher_id = teacher.id,
                    skill_id = random.choice(skills).id,
                    start_time= start,
                    end_time = end,
                    hourly_rate = round(random.uniform(20,100),2),
                )

                db.session.add(sess)


        test_user = User(
            email='some@gmail.com',
            password=bcrypt.generate_password_hash('123').decode('utf-8'),
            name=fake.name(),
            bio='test acc',
            is_teacher=True
        )
        db.session.add(test_user)
        db.session.commit()

        python_skill = db.session.execute(select(Skill).where(Skill.name == 'Python')).scalar()
        english_skill = db.session.execute(select(Skill).where(Skill.name == 'English')).scalar()
        if python_skill:
            test_user.skills.append(python_skill)
        if english_skill:
            test_user.skills.append(english_skill)
        db.session.commit()

        other_users = db.session.execute(select(User).where(User.id != test_user.id)).scalars().all()

        for reviewer in other_users[:5]:
            review = Review(
                comment=fake.paragraph(),
                reviewer_id=reviewer.id,
                teacher_id=test_user.id,
                rating=random.choice([4, 5])
            )
            db.session.add(review)
        db.session.commit()

        students = [u for u in other_users if not u.is_teacher]
        

        test_skills = [s for s in [python_skill, english_skill] if s is not None]
        test_sessions = []

        for i in range(5):
            start = fake.date_time_between(start_date='now', end_date='+6d')
            end = start + timedelta(hours=1)
            random_skill = random.choice(test_skills)
            
            sess = Sess(
                teacher_id=test_user.id,
                skill_id=random_skill.id,
                start_time=start,
                end_time=end,
                hourly_rate=random.uniform(30, 80),
                status='free'  
            )
            db.session.add(sess)
            test_sessions.append(sess)
        db.session.commit()

        for session in test_sessions:
            db.session.refresh(session)
            

        for i, session in enumerate(test_sessions[:3]):  
            if i < len(students) and session.start_time > datetime.now():
                student = students[i]
                skill = db.session.execute(select(Skill).where(Skill.id == session.skill_id)).scalar()
                skill_name = skill.name if skill else 'this skill'
                
                request = SessionRequest(
                    session_id=session.id,
                    student_id=student.id,
                    student_level=random.choice(['Beginner', 'Intermediate', 'Advanced']),
                    student_goals=f"I want to learn {skill_name}!",
                    status='pending'
                )
                db.session.add(request)

        for i, session in enumerate(test_sessions[3:4]):  
            if i < len(students):
                session.student_id = students[i].id
                session.status = 'booked'
                db.session.add(session)

        for i, session in enumerate(test_sessions[4:5]):  
            if i < len(students) and session.start_time > datetime.now():
                session.student_id = students[i].id
                session.status = 'finished'
                session.start_time = datetime.now() - timedelta(days=5)
                session.end_time = session.start_time + timedelta(hours=1)
                db.session.add(session)


        db.session.commit()