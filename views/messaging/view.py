from typing import List, Optional as OptionalTip
from datetime import datetime, timedelta
from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, select, DateTime,func, delete, distinct

from models import User, Message

from flask_bcrypt import Bcrypt

from base import BaseMethodView
from flask_login import login_user, current_user, login_required, logout_user


class ChatView(BaseMethodView):
    @login_required
    def get(self, user_id=None):
        other_user = None
        messages = []

        sent_to = self.engine.session.execute(
            select(distinct(Message.receiver_id)).where(Message.sender_id == current_user.id)
        ).scalars().all()

        received_from = self.engine.session.execute(
            select(distinct(Message.sender_id)).where(Message.receiver_id == current_user.id)
        ).scalars().all()

        user_ids = set(sent_to) | set(received_from)

        users = []

        for uid in user_ids:
            user = self.engine.session.get(User, uid)
            if user:
                users.append(user)


        if user_id:
            other_user = self.engine.session.execute(
                select(User).where(User.id == user_id)
            ).scalar_one_or_none()

            if other_user:
                messages = self.engine.session.execute(
                    select(Message).where(
                        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
                        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
                    ).order_by(Message.created_at)
                ).scalars().all()

        return render_template('chat.html', users=users, other_user=other_user, messages=messages)