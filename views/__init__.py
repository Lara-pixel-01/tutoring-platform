from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

from views.authorisation.view import SignInView, SignUpView, LogoutView
from views.dashboard.view import UserDashboardView, StudentDashboardView
from views.lessons.view import MakeSessView, DeleteSessionView, TeacherSessionsView
from views.mainpage.view import MainPageView
from views.profile.view import UserPage, EditSettingView, DeleteAccountView
from views.reviews.view import ReviewView, EditReview, DeleteReview

from views.mainpage.api import SortTeacherApi, SortByPriceAscAPI, SortByPriceDescAPI

from views.profile.api import UserProfileApi

from views.lessons.api import MyLessonsApi

from views.auth_oauth.view import GoogleLoginView, GoogleCallbackView, GitHubLoginView, GitHubCallbackView

from views.messaging.view import ChatView

from views.notifications.api import NotificationApi, UnreadCountApi

__all__ = [
    'SignInView', 'SignUpView', 'LogoutView', 'UserDashboardView', 'MakeSessView', 'DeleteSessionView',
    'UserPageView', 'EditSettingView', 'ReviewView', 'MainPageView', 'UserPage',
    'SortTeacherApi', 'SortByPriceAscAPI', 'SortByPriceDescAPI', 'UserProfileApi', 'MyLessonsApi', 'EditReview', 'DeleteReview',
    'GoogleLoginView', 'GoogleCallbackView', 'GitHubLoginView', 'GitHubCallbackView', 'TeacherSessionsView', 'ChatView', 'StudentDashboardView',
    'NotificationApi', 'UnreadCountApi', 'DeleteAccountView'
]
