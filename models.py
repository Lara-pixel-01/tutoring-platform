import random
from typing import List, Optional as OptionalTip
from faker import Faker
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
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




class User(UserMixin , db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    email: Mapped[str] = mapped_column(db.String(100), unique=True)
    password: Mapped[str] = mapped_column(db.String(100))
    name: Mapped[str] = mapped_column(db.String(100))
    bio: Mapped[OptionalTip[str]] = mapped_column(db.String(999))
    profile_pic: Mapped[OptionalTip[str]] = mapped_column(db.String(999))
    is_teacher: Mapped[bool] = mapped_column(db.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    timezone: Mapped[OptionalTip[str]] = mapped_column(db.String(50), default='UTC')  #note to self!!!!!: this will probably will come in handy when I will deal timezone convertions 

    #seperation purposes, below are the relationships:

    skills: Mapped[List["Skill"]] = relationship(secondary=user_skills, back_populates='users')

    reviews_written: Mapped[List["Review"]] = relationship(foreign_keys="Review.reviewer_id", back_populates="reviewer")
    reviews_received: Mapped[List["Review"]] = relationship(foreign_keys="Review.teacher_id", back_populates="teacher")

    portfolio: Mapped[List["PortfolioPosts"]] = relationship(back_populates='user')

    sent_messages: Mapped[List["Message"]] = relationship(foreign_keys="Message.sender_id", back_populates="sender")
    received_messages: Mapped[List["Message"]] = relationship(foreign_keys="Message.receiver_id", back_populates="receiver")

    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)




class Skill(db.Model):
    __tablename__ = 'skills'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100))
    category: Mapped[str] = mapped_column(db.String(100))
    
    #seperation purposes, below are the relationships:
    users: Mapped[List['User']] = relationship(secondary=user_skills, back_populates='skills')




class SessionRequest(db.Model):
    __tablename__ = 'session_requests'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey('sessions.id'))
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    student_level: Mapped[str] = mapped_column(db.String(100)) # later could make this selectable, like beginner, intermidiate and professional etc
    student_goals: Mapped[OptionalTip[str]] = mapped_column(db.String(1999))
    status: Mapped[str] =  mapped_column(db.String(200), default='pending')

    #seperation purposes, below are the relationships:
    session: Mapped["Sess"] = relationship(back_populates='session_requests')




class Sess(db.Model):
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





class Review(db.Model):
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



class PortfolioPosts(db.Model):
    __tablename__ = "portfolio_posts"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    text: Mapped[OptionalTip[str]] =  mapped_column(db.String(2000))
    image: Mapped[str] =  mapped_column(db.String(255)) # note to self to remember store it as a reference
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    #seperation purposes, below are the relationships:

    user: Mapped["User"] = relationship(back_populates="portfolio")



class Message(db.Model):
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



class Notification(db.Model):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    text: Mapped[str] =  mapped_column(db.String(999))
    is_seen: Mapped[bool] = mapped_column(db.Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="notifications")


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


        
        
        db.session.commit()
