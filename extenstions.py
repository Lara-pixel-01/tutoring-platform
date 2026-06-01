from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_socketio import SocketIO
from authlib.integrations.flask_client import OAuth

api = Api()

db = SQLAlchemy()

socketio = SocketIO()
oauth = OAuth()

login_manager = LoginManager()
login_manager.login_view = 'signin'