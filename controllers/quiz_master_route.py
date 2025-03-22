from flask import render_template, redirect, flash, url_for, jsonify, request
from app import app, db
from flask_login import login_required, current_user, login_user
from models.models import Subject, Chapter, Quiz, Question, User
from controllers.forms import AddChapterForm, AddSubjectForm, AddQuizForm, AddQuestionForm
from controllers import data_process


@app.route('/quiz-master/admin')
@login_required
def quiz_master_dashboard():
    if current_user.role == 'quiz-master':
        stats_master = data_process.stats_master_fun()
        return render_template('admin_dashboard.html',stats_master=stats_master)
    else:
        return {"message": "Permission denied"}, 403
    
@app.route('/quiz-master/manage-user')
@login_required
def manage_user():
    if current_user.role == 'quiz-master':
        users = User.query.filter_by(role='user').all()
        return render_template('manage_user.html',users=users)
    else:
        return {"message": "Permission denied"}, 403

@app.route('/quiz-master/user/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    if current_user.role == 'quiz-master':
        user = User.query.get(user_id)
        if user:
            return jsonify({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    else:
        return {"message": "Permission denied"}, 403
    
@app.route('/quiz-master/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role == 'quiz-master':
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    else:
        return {"message": "Permission denied"}, 403

@app.route('/quiz-master/action-sub-chap')
@login_required
def quiz_master():
    if current_user.role == 'quiz-master':
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        return render_template('quiz-master.html', subjects=subjects, chapters=chapters)
    return {"message": "Permission denied"}, 403

@app.route('/quiz-master/quiz-dashborad')
@login_required
def view_quiz_master_quiz():
    if current_user.role == 'quiz-master':
        quizzes = Quiz.query.all()
        questions = Question.query.all()
        return render_template('quiz_master_view_quiz.html', quizzes = quizzes, questions=questions)
    return {"message": "Permission denied"}, 403

@app.route('/quiz-master/add-subject',methods=['GET','POST'])
@login_required
def add_subject():
    if current_user.role == 'quiz-master':
        form = AddSubjectForm()
        if form.validate_on_submit():
            new_subject = Subject(
                name = form.subject_name.data,
                description = form.description.data
            )
            db.session.add(new_subject)
            db.session.commit()
            flash('New Subject added Sucessfully!', category='success')
            return redirect(url_for('quiz_master'))
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'The error found: {err_msg}','danger')
        return render_template('add_subject.html', form=form)
    
    else:
        return {"message": "Permission denied"}, 403
    
@app.route('/quiz-master/add-chapter',methods=['GET','POST'])
@login_required
def add_chapter():
    if current_user.role =='quiz-master':
        form = AddChapterForm()
        form.subject_id.choice = [(subject.id, subject.name) for subject in Subject.query.all()]
        if form.validate_on_submit():
            new_chapter = Chapter(
                name = form.chapter_name.data,
                description = form.description.data,
                subject_id = form.subject_id.data   
            )
            db.session.add(new_chapter)
            db.session.commit()
            flash('New chapter added Sucessfully!', category='success')
            return redirect(url_for('quiz_master'))
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'The error found: {err_msg}', 'danger')
        return render_template('add_chapter.html', form=form)
    else:
        return {"message": "Permission denied"}, 403
    

@app.route('/quiz-master/add-quiz',methods=['GET','POST'])
@login_required
def add_quiz():
    if current_user.role =='quiz-master':
        form = AddQuizForm()
        form.chapter_id.choices = [(chapter.id, chapter.name) for chapter in Chapter.query.all()]
        if form.validate_on_submit():
            new_quiz = Quiz(
                chapter_id = form.chapter_id.data,
                title = form.title.data,
                date_of_quiz = form.date_of_quiz.data,
                time_duration = form.time_duration.data,
                remark = form.remark.data   
            )
            db.session.add(new_quiz)
            db.session.commit()
            flash('New Quiz added Sucessfully!', category='success')
            return redirect(url_for('view_quiz_master_quiz'))
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'The error found: {err_msg}', 'danger')
        return render_template('add_quiz.html', form=form)
    else:
        return {"message": "Permission denied"}, 403

@app.route('/quiz-master/add-question', methods=['GET','POST'])
@login_required
def add_question():
    if current_user.role =='quiz-master':
        form = AddQuestionForm()
        form.quiz_id.choice = [(quiz.id, quiz.title) for quiz in Quiz.query.all()]
        if form.validate_on_submit():
            new_question = Question(
                quiz_id = form.quiz_id.data,
                question_statement = form.question_statement.data,
                option1 = form.option1.data,
                option2 = form.option2.data,
                option3 = form.option3.data,
                option4 = form.option4.data,
                correct_option = form.correct_option.data  
            )
            db.session.add(new_question)
            db.session.commit()
            flash('New Question added Sucessfully!', category='success')
            return redirect(url_for('view_quiz_master_quiz'))
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'The error found: {err_msg}', 'danger')
        return render_template('add_question.html', form=form)
    else:
        return {"message": "Permission denied"}, 403
    

# deletion route

@app.route('/quiz-master/subject/<int:id>',methods=['GET','POST','DELETE'])
@login_required
def modify_subject(id):
    if current_user.role =='quiz-master':
        subject = Subject.query.get(id)
        if request.method=='DELETE':
            if subject:
                if Chapter.query.filter_by(subject_id=id).first():
                    return jsonify({'message': 'This subject has chapter cannot be deleted successfully'}), 400
                db.session.delete(subject)
                db.session.commit()
                return jsonify({'message': 'Task deleted successfully'}), 200
            else:
                return jsonify({'message': 'Task not found'}), 404 
    else:
        return {"message": "Permission denied"}, 403

@app.route('/quiz-master/chapter/<int:id>',methods=['GET','POST','DELETE'])
@login_required
def modify_chapter(id):
    if current_user.role == 'quiz-master':
        chapter = Chapter.query.get(id)
        if request.method == 'DELETE':
            if chapter:
                if Quiz.query.filter_by(chapter_id=id).first():
                    return jsonify({'message': 'This chapter has quiz cannot be deleted successfully'}), 400
                db.session.delete(chapter)
                db.session.commit()
                return jsonify({'message': 'Chapter deleted successfully'}), 200
            else:
                return jsonify({'message': 'Chapter not found'}), 404
    else:
        return {"message": "Permission denied"}, 403
    
@app.route('/quiz-master/quiz/<int:id>',methods=['GET','POST','DELETE'])
@login_required
def modify_quiz(id):
    if current_user.role == 'quiz-master':
        quiz = Quiz.query.get(id)
        if request.method == 'DELETE':
            if quiz:
                if Question.query.filter_by(quiz_id=id).first():
                    return jsonify({'message': 'This chapter has quiz cannot be deleted successfully'}), 400
                db.session.delete(quiz)
                db.session.commit()
                return jsonify({'message': 'Quiz deleted successfully'}), 200
            else:
                return jsonify({'message': 'Quiz not found'}), 404
    else:
        return {"message": "Permission denied"}, 403
    
@app.route('/quiz-master/question/<int:id>',methods=['GET','POST','DELETE'])
@login_required
def modify_question(id):
    if current_user.role == 'quiz-master':
        question = Question.query.get(id)
        if request.method == 'DELETE':
            if question:
                db.session.delete(question)
                db.session.commit()
                return jsonify({'message': 'Question deleted successfully'}), 200
            else:
                return jsonify({'message': 'Question not found'}), 404
    else:
        return {"message": "Permission denied"}, 403
    
# edit route
@app.route('/quiz-master/edit-question/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_question(id):
    if current_user.role == 'quiz-master':
        question = Question.query.get(id)
        if not question:
            flash("Question not found!", "danger")
            return redirect(url_for('view_quiz_master_quiz'))

        form = AddQuestionForm()  # Create form first
        form.quiz_id.choices = [(quiz.id, quiz.title) for quiz in Quiz.query.all()]
        
        if request.method == "GET":  # Only pre-fill when loading the page
            form.quiz_id.data = question.quiz_id
            form.question_statement.data = question.question_statement
            form.option1.data = question.option1
            form.option2.data = question.option2
            form.option3.data = question.option3
            form.option4.data = question.option4
            form.correct_option.data = question.correct_option

        if form.validate_on_submit():
            question.quiz_id = form.quiz_id.data
            question.question_statement = form.question_statement.data
            question.option1 = form.option1.data
            question.option2 = form.option2.data
            question.option3 = form.option3.data
            question.option4 = form.option4.data
            question.correct_option = form.correct_option.data
            db.session.commit()
            flash("Question updated successfully!", "success")
            return redirect(url_for('view_quiz_master_quiz'))

        if form.errors:
            for err_msg in form.errors.values():
                flash(f'The error found: {err_msg}', 'danger')

        return render_template('edit_question.html', form=form, question=question)
    else:
        return {"message": "Permission denied"}, 403
    

@app.route('/quiz-master/edit-quiz/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(id):
    if current_user.role == 'quiz-master':
        quiz = Quiz.query.get(id)
        if not quiz:
            flash("Quiz not found!", "danger")
            return redirect(url_for('view_quiz_master_quiz'))

        form = AddQuizForm()  # Create form first
        form.chapter_id.choices = [(chapter.id, chapter.name) for chapter in Chapter.query.all()]
        
        if request.method == "GET":  # Only pre-fill when loading the page
            form.chapter_id.data = quiz.chapter_id
            form.title.data = quiz.title
            form.date_of_quiz.data = quiz.date_of_quiz
            form.time_duration.data = quiz.time_duration
            form.remark.data = quiz.remark

        if form.validate_on_submit():
            quiz.chapter_id = form.chapter_id.data
            quiz.title = form.title.data
            quiz.date_of_quiz = form.date_of_quiz.data
            quiz.time_duration = form.time_duration.data
            quiz.remark = form.remark.data
            db.session.commit()
            flash("Quiz updated successfully!", "success")
            return redirect(url_for('view_quiz_master_quiz'))

        if form.errors:
            for err_msg in form.errors.values():
                flash(f'The error found: {err_msg}', 'danger')

        return render_template('edit_quiz.html', form=form, quiz=quiz)
    else:
        return {"message": "Permission denied"}, 403


@app.route('/summary',methods=['GET','POST'])
@login_required
def summary():
    if current_user.role == 'quiz-master':
        stats_master = data_process.stats_master_fun()
        return render_template('summary.html',stats_master=stats_master)
    else:
        return {"message": "Permission denied"}, 403
