import random
from typing import List, Optional as OptionalTip
from datetime import datetime, timedelta
from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, select, DateTime,func, delete

from authlib.integrations.flask_client import OAuth

from flask_restful import Api, Resource
from pydantic import BaseModel

from models import User


from forms import *

from base import BaseMethodView
from flask_login import current_user



class MainPageView(BaseMethodView): 
    def get(self):
        stmt = select(User).where(User.is_teacher == True)
        teachers = self.engine.session.execute(stmt).scalars().all()
            
        user = current_user if current_user.is_authenticated else None

        return render_template('mainpage.html', users= teachers, user=user)