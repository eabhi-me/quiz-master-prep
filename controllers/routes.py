from flask import render_template, redirect, flash, Request, url_for
from app import app, db, api
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models.models import User
from controllers.forms import LoginForm, RegistrationFrom


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(email_address = form.email_address.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password = form.password.data):
            login_user(attempted_user)
            flash(f'Success! You have loged in as {attempted_user.email_address}', category='info')
            return redirect(url_for('quiz_master_dashboard' if attempted_user.role == 'quiz-master' else 'dashboard'))
        else:
            flash('Incorrect Email address or password', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been Logout',category='info')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationFrom()
    if form.validate_on_submit():
        new_user = User(
            email_address = form.email_address.data,
            username = form.email_address.data,
            full_name = form.full_name.data,
            qualification = form.qualification.data,
            dob = form.dob.data,
            password_hash = generate_password_hash(form.password1.data)
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))
    
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'The error found: {err_msg}','danger')
    return render_template('register.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        keyword = request.form.get('keyword')  # Use `request.form` instead of `request.args`
        if not keyword:
            return {'message': 'No search keyword provided'}, 400

        results = {}  # Initialize results dictionary
        
        if current_user.role == 'quiz-master':
            # Search in User table
            users = User.query.filter(
                (User.username.ilike(f'%{keyword}%')) |
                (User.email_address.ilike(f'%{keyword}%')) |
                (User.full_name.ilike(f'%{keyword}%'))
            ).all()

            # Search in Chapter table
            chapters = Chapter.query.filter(Chapter.name.ilike(f'%{keyword}%')).all()

            # Search in Subject table
            subjects = Subject.query.filter(Subject.name.ilike(f'%{keyword}%')).all()

            # Search in Quiz table
            quizzes = Quiz.query.filter(Quiz.title.ilike(f'%{keyword}%')).all()

            # Search in Question table
            questions = Question.query.filter(Question.question_statement.ilike(f'%{keyword}%')).all()

            results = {
                'users': users,
                'chapters': chapters,
                'subjects': subjects,
                'quizzes': quizzes,
                'questions': questions
            }
        else:
            # Search only in quizzes
            quizzes = Quiz.query.filter(Quiz.title.ilike(f'%{keyword}%')).all()
            # Search in Chapter table
            chapters = Chapter.query.filter(Chapter.name.ilike(f'%{keyword}%')).all()

            # Search in Subject table
            subjects = Subject.query.filter(Subject.name.ilike(f'%{keyword}%')).all()

            results = {
                'quizzes': quizzes,
                'subjects': subjects,
                'chapters': chapters

            }

        return render_template('search_results.html', results=results)



@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html"), 404

@app.route("/<path:unknown_path>")
def catch_all(unknown_path):
    flash('Not Found what you are looking')
    return redirect(url_for("home"))


from controllers.quiz_master_route import *
from controllers.user_route import *
from controllers.api_controllers import *