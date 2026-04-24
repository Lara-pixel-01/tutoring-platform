from flask import Flask
from flask_session import Session
from flask_bcrypt import Bcrypt
from sqlalchemy import select

from extenstions import db, login_manager
from models import User
from views import *
from models import fill_db, create_db


def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ash123@localhost:5432/skillPlatform'
    app.config['SECRET_KEY'] = 'hnDsdfjsSdfINFBVNWDVN232342342341dfsdfsfsd567cgvhjbvgcdrt4567SDSFGFBVDFthfgbv'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    
    db.init_app(app)
    create_db(app)
    fill_db(app)
    login_manager.init_app(app)
    login_manager.login_view = 'signin' 
    Session(app)
    
    bcrypt = Bcrypt(app)
    
    import views
    views.bcrypt = bcrypt
    
    @login_manager.user_loader
    def load_user(user_id: int) -> User | None:
        stmt = select(User).where(User.id == int(user_id))
        return db.session.execute(stmt).scalar_one_or_none()

    app.add_url_rule('/', view_func=MainPageView.as_view('ind', db))
    app.add_url_rule('/signup/', view_func=SignUpView.as_view('signup', db))
    app.add_url_rule('/signin/', view_func=SignInView.as_view('signin', db))
    app.add_url_rule('/settings/', view_func=EditSettingView.as_view('settings', db))
    app.add_url_rule('/dashboard/', view_func=UserDashboardView.as_view('dashboard', db))
    app.add_url_rule('/logout', view_func=LogoutView.as_view('logout', db))
    app.add_url_rule('/review/<int:teacher_id>', view_func=ReviewView.as_view('review', db))
    app.add_url_rule('/create-session', view_func=MakeSessView.as_view('make_session', db))
    
    return app

if __name__ == '__main__':
	app = create_app()
	print(app.url_map)
	app.run(port=9000, debug=True, use_reloader=False)