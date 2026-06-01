import random
from typing import List, Optional as OptionalTip
from datetime import datetime, timedelta
from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, select, DateTime,func, delete

from models import User, Skill, user_skills, SessionRequest, Sess, Review, PortfolioPosts, Message, Notification

from forms import *

from base import BaseMethodView
from flask_login import login_user, current_user, login_required, logout_user

from views import bcrypt



class ReviewView(BaseMethodView): 
    def get(self, teacher_id: int):
        
        teacher = self.engine.session.execute(
            select(User).where(User.id == teacher_id)
            ).scalar_one_or_none()
        
        if teacher is None:
            flash('No such user', 'error')
            return redirect(url_for('ind'))
        
        form = ReviewForm()

        reviews = self.engine.session.execute(select(Review).where(Review.teacher_id == teacher_id)).scalars().all()
        
        for review in reviews:
            review.reviewer = self.engine.session.execute(
                select(User).where(User.id == review.reviewer_id)
                ).scalar_one_or_none()

        return render_template('review.html', form=form, reviews=reviews, teacher=teacher)
    


    @login_required
    def post(self, teacher_id:int):
        form = ReviewForm()

        if form.validate_on_submit():
            review = Review(
                comment= form.comment.data,
                reviewer_id = current_user.id,
                teacher_id=teacher_id,
                rating = form.rating.data
            )

            self.engine.session.add(review)
            self.engine.session.commit()
            
            return redirect(url_for('review', teacher_id=teacher_id))
        
        return redirect(url_for('review', teacher_id=teacher_id))
    

class DeleteReview(BaseMethodView):
    @login_required 
    def post(self, review_id: int):
        deleted_rev = self.engine.session.execute(
            select(Review).where(Review.id == review_id)
        ).scalar_one_or_none()

        if not deleted_rev or deleted_rev.reviewer_id != current_user.id:
            flash('Review not found or unathorised', 'error')
            return redirect(url_for('dashboard'))
        

        teacher_id = deleted_rev.teacher_id
        self.engine.session.delete(deleted_rev)
        self.engine.session.commit()

        return redirect(url_for('review', teacher_id=teacher_id))
        


class EditReview(BaseMethodView):
    @login_required
    def get(self, review_id: int):
        review = self.engine.session.get(Review, review_id)
        
        if not review or review.reviewer_id != current_user.id:
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))
        
        form = ReviewForm()
        form.comment.data = review.comment
        form.rating.data = review.rating
        
        return render_template('edit_review.html', form=form, review=review)

    @login_required
    def post(self, review_id: int):
        review = self.engine.session.get(Review, review_id)
        
        if not review or review.reviewer_id != current_user.id:
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))
        
        review.comment = request.form.get('comment')
        review.rating = request.form.get('rating')
        self.engine.session.commit()
        flash('Review updated!', 'success')
        
        return redirect(url_for('review', teacher_id=review.teacher_id))