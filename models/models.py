from app import app, db, bcrypt, login_manager
from datetime import datetime
from pytz import timezone
from flask_bcrypt import generate_password_hash, check_password_hash
# seting the environment
from dotenv import load_dotenv
import os
load_dotenv()

# Importig the library that manage all user login method
from flask_login import UserMixin

# for time zone manage
IST = timezone('Asia/Kolkata')

class User(db.Model,UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    username = db.Column(db.String(60), nullable=False, unique=True)
    email_address = db.Column(db.String(150), unique=True, nullable=False)
    full_name = db.Column(db.String(60), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(), nullable=True)
    dob = db.Column(db.String(), nullable=True)
    role = db.Column(db.String(10), nullable=False, default='user')

    scores = db.relationship('Score', backref='user', lazy=True)

    # adding the getter and setter for hased password
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=True)

    chapters = db.relationship('Chapter', backref='subject', lazy=True)


class Chapter(db.Model):
    __tablename__ = "chapters"
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=True)
    subject_id = db.Column(db.Integer(), db.ForeignKey('subjects.id'), nullable=False)

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)


class Quiz(db.Model):
    __tablename__ = "quizzes"
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(), nullable=False)
    chapter_id = db.Column(db.Integer(), db.ForeignKey('chapters.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Time, nullable=False)
    remark = db.Column(db.String(100), nullable=True)

    questions = db.relationship('Question', backref='quiz', lazy=True)


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_statement = db.Column(db.String(), nullable=False)
    option1 = db.Column(db.String(),nullable=True)
    option2 = db.Column(db.String(),nullable=True)
    option3 = db.Column(db.String(),nullable=True)
    option4 = db.Column(db.String(),nullable=True)

    correct_option = db.Column(db.String(100), nullable=False)


class Score(db.Model):
    __tablename__ = "scores"
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    quiz_id = db.Column(db.Integer(), db.ForeignKey('quizzes.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(IST))
    total_scored = db.Column(db.Integer(), nullable=False)
    total_questions = db.Column(db.Integer(),nullable=True)


# Create the database and tables
with app.app_context():
    db.create_all()

    try:
        # Create a default admin user if none exists
        if not User.query.first():
            admin_user = [ 
                User(
                email_address='quizmaster@quiz.com',
                username='quizmaster@quiz.com',
                full_name='Quiz Master',
                password_hash=generate_password_hash(os.environ.get('SECRET_KEY')),
                role = 'quiz-master'),
                User(
                email_address='dummy@quiz.com',
                username='dummy@quiz.com',
                full_name='Dummy',
                password_hash=generate_password_hash(os.environ.get('SECRET_KEY')),
                role = 'user')
            ]
            db.session.bulk_save_objects(admin_user)
            db.session.commit()

    except Exception as e:
        print(f'An error occurred: {str(e)}')
        db.session.rollback()
    finally:
        db.session.close()
