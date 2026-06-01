from flask import Flask
from flask_session import Session
from flask_bcrypt import Bcrypt
from sqlalchemy import select

from extenstions import db, login_manager, api, socketio, oauth
from models import User
from models import fill_db, create_db
import os
from dotenv import load_dotenv
import socket_events


from views import  (MainPageView, SignUpView, SignInView, EditSettingView, UserDashboardView, 
                    LogoutView, ReviewView, MakeSessView, DeleteSessionView, SortTeacherApi, 
                    SortByPriceAscAPI, SortByPriceDescAPI, MyLessonsApi, UserProfileApi, EditReview, DeleteReview,
                    GoogleLoginView, GoogleCallbackView, GitHubLoginView, GitHubCallbackView, UserPage, TeacherSessionsView, ChatView, 
                    StudentDashboardView, NotificationApi, UnreadCountApi,DeleteAccountView)



load_dotenv()

def create_app(config: dict = None):
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ash123@db:5432/skillPlatform'
    app.config['SECRET_KEY'] = 'hnDsdfjsSdfINFBVNWDVN232342342341dfsdfsfsd567cgvhjbvgcdrt4567SDSFGFBVDFthfgbv'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['WTF_CSRF_ENABLED'] = True

    if config:
        app.config.update(config)
    
    db.init_app(app)



    create_db(app)
    fill_db(app)
    login_manager.init_app(app)
    login_manager.login_view = 'signin' 
    Session(app)

    socketio.init_app(app)
    
    bcrypt = Bcrypt(app)
    
    import views 
    views.bcrypt = bcrypt


    oauth.init_app(app)

    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )

    
    oauth.register(
        name='github',
        client_id=os.getenv('GITHUB_CLIENT_ID'),
        client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )


    
    @login_manager.user_loader
    def load_user(user_id: int) -> User | None:
        stmt = select(User).where(User.id == int(user_id))
        return db.session.execute(stmt).scalar_one_or_none()


    app.add_url_rule('/', view_func=MainPageView.as_view('ind', db))
    app.add_url_rule('/signup/', view_func=SignUpView.as_view('signup',db))
    app.add_url_rule('/signin/', view_func=SignInView.as_view('signin', db))
    app.add_url_rule('/settings/', view_func=EditSettingView.as_view('settings', db))
    app.add_url_rule('/dashboard/', view_func=UserDashboardView.as_view('dashboard',db))
    app.add_url_rule('/logout', view_func=LogoutView.as_view('logout',db))
    app.add_url_rule('/review/<int:teacher_id>', view_func=ReviewView.as_view('review',db))
    app.add_url_rule('/create-session', view_func=MakeSessView.as_view('make_session',db))
    app.add_url_rule('/delete-session/<int:session_id>', view_func=DeleteSessionView.as_view('delete_session',db))
    app.add_url_rule('/review/update/<int:review_id>', view_func=EditReview.as_view('edit_review', db))
    app.add_url_rule('/review/delete/<int:review_id>', view_func=DeleteReview.as_view('delete_review', db))
    app.add_url_rule('/login/google', view_func=GoogleLoginView.as_view('google_login', db))
    app.add_url_rule('/callback/google', view_func=GoogleCallbackView.as_view('google_callback', db))
    app.add_url_rule('/login/github', view_func=GitHubLoginView.as_view('github_login', db))
    app.add_url_rule('/callback/github', view_func=GitHubCallbackView.as_view('github_callback', db))
    app.add_url_rule('/userpage/<int:user_id>', view_func=UserPage.as_view('user_page', db))
    app.add_url_rule('/teacher/<int:user_id>/sessions', view_func=TeacherSessionsView.as_view('teacher_sessions', db))
    app.add_url_rule('/chat/', view_func=ChatView.as_view('chat', db))
    app.add_url_rule('/chat/<int:user_id>', view_func=ChatView.as_view('chat_with', db))
    app.add_url_rule('/student-dashboard', view_func=StudentDashboardView.as_view('student_dashboard', db))
    app.add_url_rule('/delete-account', view_func=DeleteAccountView.as_view('delete_account', db))

    api.add_resource(SortTeacherApi, '/api/sort_by_rating', resource_class_kwargs={'engine': db})
    api.add_resource(SortByPriceAscAPI, '/api/sort_by_price_asc', resource_class_kwargs={'engine': db})
    api.add_resource(SortByPriceDescAPI, '/api/sort_by_price_desc', resource_class_kwargs={'engine': db})

    api.add_resource(MyLessonsApi, '/api/my_lessons', resource_class_kwargs={'engine': db})
    api.add_resource(UserProfileApi, '/api/user_profile/<int:user_id>', resource_class_kwargs={'engine': db})
    api.add_resource(NotificationApi, '/api/notifications', resource_class_kwargs={'engine': db})
    api.add_resource(UnreadCountApi, '/api/notifications/unread-count', resource_class_kwargs={'engine': db})
    

    api.init_app(app)


    return app

if __name__ == '__main__':
	app = create_app()
	print(app.url_map)
	socketio.run(app, host='0.0.0.0', port=9000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)