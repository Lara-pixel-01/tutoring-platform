import pytest
from app import create_app
from extenstions import db


@pytest.fixture(scope='session')
def app():
	config = {
		'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
		'CSRF_ENABLED': False,
		'SECRET_KEY': 'sldklnkfjsebjkfbsefkjfbes',
		'TESTING': True,
		'WTF_CSRF_ENABLED': False
	}
	return create_app(config)


@pytest.fixture(scope='session')
def client(app):
	return app.test_client()

@pytest.fixture(scope='session')
def db_session(app):
	with app.app_context():
	    yield db.session

@pytest.fixture(scope='session')
def test_user(app, db_session):
	from models import User, Skill, UserSettings
	from flask_bcrypt import Bcrypt
	from sqlalchemy import select

	bcrypt = Bcrypt()

	with app.app_context():
		user = User(
			email = 'som12@gmail.com',
			password = bcrypt.generate_password_hash('1').decode('utf-8'),
			name='Connor',
			is_teacher=True
		)

		db_session.add(user)
		db_session.commit()
		settings = UserSettings(user_id=user.id)
		db_session.add(settings)
		
		s = db_session.execute(select(Skill)).first()
		skill = s[0]

		user.skills.append(skill)
		db_session.commit()

		yield user