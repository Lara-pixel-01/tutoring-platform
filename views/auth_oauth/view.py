from base import BaseMethodView
from flask import flash, redirect, url_for
from flask_login import login_user
from sqlalchemy import select
from models import User, UserSettings
from extenstions import oauth
from views import bcrypt
import secrets


class GoogleLoginView(BaseMethodView):
    def get(self):
        redirect_uri = url_for('google_callback', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)


class GoogleCallbackView(BaseMethodView):
    def get(self):
        try:
            token = oauth.google.authorize_access_token()
            user_info = token.get('userinfo')
            
            if not user_info:
                resp = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo')
                user_info = resp.json()
            
            email = user_info.get('email')
            name = user_info.get('name', email.split('@')[0])

            user = self.engine.session.execute(
                select(User).where(User.email == email)).scalar_one_or_none()
            
            if not user:
                random_password = secrets.token_urlsafe(16)
                password_hashed = bcrypt.generate_password_hash(random_password).decode('utf-8')
                
                user = User(
                    email=email,
                    name=name,
                    password=password_hashed,
                    is_teacher=False
                )
                self.engine.session.add(user)
                self.engine.session.commit()

                settings = UserSettings(user_id=user.id)
                self.engine.session.add(settings)
                self.engine.session.commit()
            
            login_user(user)
            flash(f'Welcome, {user.name}!', 'success')
            return redirect(url_for('ind'))
            
        except Exception as e:
            flash(f'Authentication failed: {str(e)}', 'error')
            return redirect(url_for('signin'))


class GitHubLoginView(BaseMethodView):
    def get(self):
        redirect_uri = url_for('github_callback', _external=True)
        return oauth.github.authorize_redirect(redirect_uri)


class GitHubCallbackView(BaseMethodView):
    def get(self):
        try:
            token = oauth.github.authorize_access_token()
            resp = oauth.github.get('user', token=token)
            user_info = resp.json()
            
            email = user_info.get('email')
            if not email:
                emails_resp = oauth.github.get('user/emails', token=token)
                emails = emails_resp.json()
                email = emails[0]['email'] if emails else None
            
            if not email:
                flash('Could not get email from GitHub', 'error')
                return redirect(url_for('signin'))
            
            name = user_info.get('name') or user_info.get('login') or email.split('@')[0]

            user = self.engine.session.execute(
                select(User).where(User.email == email)).scalar_one_or_none()
            
            if not user:
                random_password = secrets.token_urlsafe(16)
                password_hashed = bcrypt.generate_password_hash(random_password).decode('utf-8')
                
                user = User(
                    email=email,
                    name=name,
                    password=password_hashed,
                    is_teacher=False
                )
                self.engine.session.add(user)
                self.engine.session.commit()
                
                settings = UserSettings(user_id=user.id)
                self.engine.session.add(settings)
                self.engine.session.commit()
            
            login_user(user)
            flash(f'Welcome, {user.name}!', 'success')
            return redirect(url_for('ind'))
            
        except Exception as e:
            flash(f'GitHub authentication failed: {str(e)}', 'error')
            return redirect(url_for('signin'))