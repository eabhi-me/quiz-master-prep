from flask import render_template, redirect, flash, url_for, jsonify, request, session
from app import app, db
from flask_login import login_required, current_user, login_user
from models.models import Subject, Chapter, Quiz, Question, Score
from controllers.forms import QuizAttemptForm
from datetime import datetime, timedelta
# imporitg the functin of data process
from controllers.data_process import user_stats



@app.route('/dashboard')
@login_required
def dashboard():
    upcoming_quizzes = Quiz.query.filter(Quiz.date_of_quiz > datetime.now()).all()
    old_quizzes = Quiz.query.filter(Quiz.date_of_quiz <= datetime.now()).all()
    quizzes = {
        "upcoming": upcoming_quizzes,
        "old": old_quizzes
    }
    return render_template('dashboard.html',quizzes=quizzes)

@app.route('/view-quiz/<int:quiz_id>')
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    if not quiz:
        flash("Quiz not found", "danger")
        return redirect(url_for("dashboard"))
    chapter = Chapter.query.filter_by(id=quiz.chapter_id).first()
    chapter_name = chapter.name if chapter else "Unknown Chapter"
    nos_of_questions = Question.query.filter_by(quiz_id=quiz_id).count()
    return render_template("view_quiz.html", quiz=quiz, nos_of_questions=nos_of_questions, chapter_name=chapter_name)


@app.route("/attempt-quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def attempt_quiz(quiz_id):
     # Check again to prevent bypassing the restriction
    previous_attempt = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    if previous_attempt:
        flash('You have already attempt the quiz',category='info')
        return redirect(url_for('view_result', quiz_id=quiz_id))  # Redirect if already attempted
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    quiz = Quiz.query.filter_by(id=quiz_id).first()

    if 'quiz_start_time' not in session:
        session['quiz_start_time'] = datetime.now().isoformat()

    # Calculate end time
    quiz_start_time = datetime.fromisoformat(session['quiz_start_time'])
    duration_in_minutes = quiz.time_duration.hour * 60 + quiz.time_duration.minute

    # Calculate quiz end time
    quiz_end_time = quiz_start_time + timedelta(minutes=duration_in_minutes)
    
    if "current_question" not in session:
        session["current_question"] = 0  # Start from first question
        session["answers"] = {}  # Store answers

    current_index = session["current_question"]

    if current_index >= len(questions):
        return redirect(url_for("quiz_result", quiz_id=quiz_id))  # Redirect to result

    question = questions[current_index]
    form = QuizAttemptForm()

    # Set option choices dynamically
    form.selected_option.choices = [
        (question.option1, question.option1),
        (question.option2, question.option2),
        (question.option3, question.option3),
        (question.option4, question.option4)
    ]

    # Check if previous answer exists
    if str(current_index) in session["answers"]:
        form.selected_option.data = session["answers"][str(current_index)]

    if form.validate_on_submit():
        session["answers"][str(current_index)] = form.selected_option.data  # Store answer

        if form.next.data and current_index < len(questions) - 1:  
            session["current_question"] += 1
        elif form.prev.data and current_index > 0:
            session["current_question"] -= 1
        elif form.submit.data:
            session["answers"][str(current_index)] = form.selected_option.data
            session.modified = True # this is must for as store that session is complete, this take 1h to fix 
            return redirect(url_for("quiz_result", quiz_id=quiz_id))

        return redirect(url_for("attempt_quiz", quiz_id=quiz_id))

    return render_template("attempt_quiz.html", form=form, question=question, current_index=current_index, total=len(questions), quiz_end_time=quiz_end_time, quiz_id=quiz.id)


@app.route("/quiz-result/<int:quiz_id>")
@login_required
def quiz_result(quiz_id):
    previous_attempt = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    if previous_attempt:
        flash('You have already attempt the quiz',category='info')
        return redirect(url_for('view_result', quiz_id=quiz_id))  # Redirect if already attempted
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    answers = session.get("answers", {})
    score = 0
    user_answers = dict(answers)  # Copy answers before clearing session

    for i, question in enumerate(questions):
        if str(i) in answers and str(answers[str(i)]) == str(question.correct_option):
            score += 1

    new_score = Score(
        user_id=current_user.id,
        quiz_id=quiz_id,
        total_scored=score,
        total_questions = len(questions)
    )
    db.session.add(new_score)
    db.session.commit()
    flash(f"You scored {score}/{len(questions)}", "success")

    # Clear session after storing data
    session.pop("current_question", None)
    session.pop("answers", None)
    session.pop('quiz_start_time', None)

    return render_template(
        "quiz_result.html",
        score=score,
        total=len(questions),
        questions=questions,
        user_answers=user_answers  # Pass user answers to the template
    )

@app.route('/view-result')
@login_required
def view_result():
    user_scores = Score.query.filter_by(user_id=current_user.id).all()
    quiz_details = []
    for score in user_scores:
        quiz = Quiz.query.filter_by(id=score.quiz_id).first()
        if quiz:
            chapter = Subject.query.filter_by(id=quiz.chapter_id).first()
            quiz_details.append({
                "quiz_name": quiz.title,
                "subject_name": chapter.name if chapter else "Unknown Subject",
                "score": score.total_scored,
                "total_questions": score.total_questions,
                "time": score.time_stamp_of_attempt  # Assuming you have a timestamp field in Score model
            })
    if not user_scores:
        flash('User has not attempted any quiz:', 'danger')
    return render_template('view_result.html', user_scores=user_scores, quiz_details=quiz_details)

@app.route('/summary/user')
@login_required
def user_summary():
    if current_user.role == 'user':
        user_id = current_user.id
        user_stats_data = user_stats(user_id)
        return render_template('user_summary.html', user_stats_data=user_stats_data, user_name=current_user.full_name)
