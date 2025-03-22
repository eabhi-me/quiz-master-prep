from flask import request, jsonify
from flask_restful import Resource
from app import api,db
from models.models import User, Chapter, Subject, Quiz, Question
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
from flasgger import swag_from

class UserResource(Resource):
    @swag_from('docs/user_get.yml')
    def get(self, id=None):
        if id:
            user = User.query.filter_by(id=id).first()
            if user:
                return {'id':user.id,'username':user.username, 'email_address':user.email_address, 'full_name':user.full_name}, 200
            else:
                return {'message': 'User not found'}, 404
        else:
            users = User.query.all()
            if users:
                users_list = [{'id': user.id, 'username': user.username, 'email_address': user.email_address, 'full_name': user.full_name} for user in users]
                return users_list, 200
            else:
                return {'message':'No User Exist'}, 200
    @swag_from('docs/user_post.yml')    
    def post(self):
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        if isinstance(data, list):
            users = []
            for user_data in data:
                username = user_data.get('username')
                email_address = user_data.get('email_address')
                full_name = user_data.get('full_name')
                password_hash = generate_password_hash(user_data.get('password_hash'))

                if not username or not email_address or not full_name:
                    return {'message': 'Missing required fields in one of the users'}, 400

                new_user = User(username=username, email_address=email_address, full_name=full_name, password_hash=password_hash)
                users.append(new_user)
                db.session.add(new_user)
            db.session.commit()
            return {'message': 'Users created successfully', 'ids': [user.id for user in users]}, 201
        else:
            username = data.get('username')
            email_address = data.get('email_address')
            full_name = data.get('full_name')
            password_hash = generate_password_hash(data.get('password_hash'))

            if not username or not email_address or not full_name:
                return {'message': 'Missing required fields'}, 400

            new_user = User(username=username, email_address=email_address, full_name=full_name, password_hash=password_hash)
            db.session.add(new_user)
            db.session.commit()

            return {'message': 'User created successfully', 'id': new_user.id}, 201
    @swag_from('docs/user_patch.yml')
    def patch(self, id):
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        user = User.query.filter_by(id=id).first()
        if not user:
            return {'message': 'User not found'}, 404

        username = data.get('username')
        email_address = data.get('email_address')
        full_name = data.get('full_name')
        password_hash = data.get('password_hash')

        if username:
            user.username = username
        if email_address:
            user.email_address = email_address
        if full_name:
            user.full_name = full_name
        if password_hash:
            user.password_hash = generate_password_hash(password_hash)

        db.session.commit()
        return {'message': 'User updated successfully'}, 200
    @swag_from('docs/user_delete.yml')
    def delete(self, id):
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'Success'}, 200
        else:
            return {'message': 'User not found'}, 404


class SubjectResource(Resource):
    @swag_from('docs/subject_get.yml')
    def get(self, id=None):
        if id:
            subject = Subject.query.get(id)
            if subject:
                return {'id':subject.id, 'name':subject.name, 'description':subject.description, 'chapter':subject.chapters}, 200
            else:
                return {'message':'Not Found'}, 404
        else:
            subjects = Subject.query.all()
            if subjects:
                subject_list = [{'id':subject.id,'name':subject.name,'description':subject.description} for subject in subjects]
                return subject_list, 200
            else:
                return {'message':'No chapeter exist'}, 200
    @swag_from('docs/subject_post.yml')
    def post(self):
        data = request.get_json()
        if not data:
            return {'message':'Data Not found'},400
        if isinstance(data, list):
            subjects = []
            for subject_data in data:
                name = subject_data.get('name')
                description = subject_data.get('description')
                
                if not name:
                    return {'message':'Misssing required feilds'}, 400
                new_subject = Subject(name=name,description=description)
                subjects.append(new_subject)
                db.session.add(new_subject)
            db.session.commit()
            return {'message':'Data Added Successfully', 'ids': [subject.id for subject in subjects]}, 201
        else:
            name = data.get('name')
            description = data.get('description')
            new_subject = Subject(name=name,description=description)
            db.session.add(new_subject)
            db.session.commit()
            return {'message': 'user created successfully','id': new_subject.id}, 201
    @swag_from('docs/subject_patch.yml')
    def patch(self, id):
        data = request.get_json()
        if not data:
            return {'message':'No Input data provided'}, 400

        subject = Subject.query.filter_by(id=id).first()
        if not subject:
            return {'message':'Chapter Not found'}, 404

        name = data.get('name')
        description = data.get('description')

        if name:
            subject.name = name
        if description:
            subject.description = description

        db.session.commit()
        return {'message':'chapter update successfully'}, 200

    @swag_from('docs/subject_delete.yml')
    def delete(self, id):
        subject = Subject.query.filter_by(id=id).first()
        if subject:
            db.session.delete(subject)
            db.session.commit()
            return {'message':'Success'},200
        else:
            return {'message':'User Not found'},404            

class ChapterResource(Resource):
    @swag_from('docs/chapter_get.yml')
    def get(self, id=None):
        if id:
            chapter = Chapter.query.get(id)
            if chapter:
                return {'id': chapter.id, 'name': chapter.name, 'subject_id': chapter.subject_id, 'description':chapter.description}, 200
            else:
                return {'message': 'Chapter not found'}, 404
        else:
            chapters = Chapter.query.all()
            if chapters:
                chapter_list = [{'id': chapter.id, 'name': chapter.name, 'subject_id': chapter.subject_id, 'description':chapter.description} for chapter in chapters]
                return chapter_list, 200
            else:
                return {'message': 'No chapters exist'}, 200
            
    @swag_from('docs/chapter_post.yml')
    def post(self):
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        if isinstance(data, list):
            chapters = []
            for chapter_data in data:
                name = chapter_data.get('name')
                subject_id = chapter_data.get('subject_id')
                description =  chapter_data.get('description')

                if not name or not subject_id:
                    return {'message': 'Missing required fields in one of the chapters'}, 400

                new_chapter = Chapter(name=name, subject_id=subject_id, description=description)
                chapters.append(new_chapter)
                db.session.add(new_chapter)
            db.session.commit()
            return {'message': 'Chapters created successfully', 'ids': [chapter.id for chapter in chapters]}, 201
        else:
            name = data.get('name')
            subject_id = data.get('subject_id')
            description =  chapter_data.get('description')

            if not name or not subject_id:
                return {'message': 'Missing required fields'}, 400

            new_chapter = Chapter(name=name, subject_id=subject_id,description=description)
            db.session.add(new_chapter)
            db.session.commit()

            return {'message': 'Chapter created successfully', 'id': new_chapter.id}, 201
        
    @swag_from('docs/chapter_patch.yml')
    def patch(self, id):
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        chapter = Chapter.query.filter_by(id=id).first()
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        name = data.get('name')
        subject_id = data.get('subject_id')
        description =  data.get('description')

        if name:
            chapter.name = name
        if subject_id:
            chapter.subject_id = subject_id
        if description:
            chapter.description = description
        db.session.commit()
        return {'message': 'Chapter updated successfully'}, 200
    
    @swag_from('docs/chapter_delete.yml')
    def delete(self, id):
        chapter = Chapter.query.filter_by(id=id).first()
        if chapter:
            db.session.delete(chapter)
            db.session.commit()
            return {'message': 'Success'}, 200
        else:
            return {'message': 'Chapter not found'}, 404

class QuizResource(Resource):
    @swag_from('docs/quiz_get.yml')
    def get(self,id=None):
        if id:
            quiz = Quiz.query.get(id=id).first()
            if quiz:
                return {'id':quiz.id, 'title':quiz.title,'chapter_id':quiz.chpater_id,'date_of_quiz':str(quiz.date_of_quiz),'time_duration':str(quiz.time_duration),'remark':quiz.remark}, 200
            else:
                return {'message':'Not Found'}, 404
        else:
            quizs = Quiz.query.all()
            if quizs:
                quizs_list = [{'id':quiz.id, 'title':quiz.title,'chapter_id':quiz.chapter_id,'date_of_quiz':str(quiz.date_of_quiz),'time_duration':str(quiz.time_duration),'remark':quiz.remark} for quiz in quizs]
                return quizs_list, 200

    @swag_from('docs/quiz_post.yml')        
    def post(self):
        data = request.get_json()
        if not data:
            return {'message':'No Input data'}, 400
        if isinstance(data, list):
            quizzes = []
            for quiz_data in data:
                title = quiz_data.get('title')
                chapter_id = quiz_data.get('chapter_id')
                date_of_quiz = datetime.strptime(quiz_data.get('date_of_quiz'), '%Y-%m-%d')
                time_duration = datetime.strptime(quiz_data.get('time_duration'), '%H:%M:%S').time()
                remark = quiz_data.get('remark')

                if not title or not chapter_id or not date_of_quiz or not time_duration:
                    return {'message': 'Missing required fields in one of the quizzes'}, 400

                new_quiz = Quiz(title=title, chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration, remark=remark)
                quizzes.append(new_quiz)
                db.session.add(new_quiz)
            db.session.commit()
            return {'message': 'Quizzes created successfully', 'ids': [quiz.id for quiz in quizzes]}, 201
        else:
            title = data.get('title')
            chapter_id = data.get('chapter_id')
            date_of_quiz = datetime.strptime(data.get('date_of_quiz'), '%Y-%m-%d')
            time_duration = datetime.strptime(data.get('time_duration'), '%H:%M:%S').time()
            remark = data.get('remark')

            if not title or not chapter_id or not date_of_quiz or not time_duration:
                return {'message': 'Missing required fields'}, 400

            new_quiz = Quiz(title=title, chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration, remark=remark)
            db.session.add(new_quiz)
            db.session.commit()

            return {'message': 'Quiz created successfully', 'id': new_quiz.id}, 201

    @swag_from('docs/quiz_patch.yml')
    def patch(self, id):
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        quiz = Quiz.query.filter_by(id=id).first()
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        title = data.get('title')
        chapter_id = data.get('chapter_id')
        date_of_quiz = data.get('date_of_quiz')
        time_duration = data.get('time_duration')
        remark = data.get('remark')

        if title:
            quiz.title = title
        if chapter_id:
            quiz.chapter_id = chapter_id
        if date_of_quiz:
            quiz.date_of_quiz = date_of_quiz
        if time_duration:
            quiz.time_duration = time_duration
        if remark:
            quiz.remark = remark

        db.session.commit()
        return {'message': 'Quiz updated successfully'}, 200

    @swag_from('docs/quiz_delete.yml')
    def delete(self, id):
        quiz = Quiz.query.filter_by(id=id).first()
        if quiz:
            db.session.delete(quiz)
            db.session.commit()
            return {'message': 'Success'}, 200
        else:
            return {'message': 'Quiz not found'}, 404

class QuestionResource(Resource):
    @swag_from('docs/question_get.yml')
    def get(self, id=None):
        if id:
            question = Question.query.get(id)
            if question:
                return {'id': question.id, 'quiz_id': question.quiz_id, 'question_statement': question.question_statement, 'options': [question.option1,question.option2,question.option3,question.option4,], 'answer': question.correct_option}, 200
            else:
                return {'message': 'Question not found'}, 404
        else:
            questions = Question.query.all()
            if questions:
                question_list = [{'id': question.id, 'quiz_id': question.quiz_id, 'question_statement': question.question_statement, 'options': [question.option1,question.option2,question.option3,question.option4,], 'answer': question.correct_option} for question in questions]
                return question_list, 200
            else:
                return {'message': 'No questions exist'}, 200

    @swag_from('docs/question_post.yml')
    def post(self):
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        if isinstance(data, list):
            questions = []
            for question_data in data:
                quiz_id = question_data.get('quiz_id')
                question_statement = question_data.get('question_statement')
                options = question_data.get('options')
                option1 = options[0]
                option2 = options[1]
                option3 = options[2]
                option4 = options[3]
                correct_option = question_data.get('correct_option')

                if not quiz_id or not question_statement or not options or not correct_option:
                    return {'message': 'Missing required fields in one of the questions'}, 400

                new_question = Question(quiz_id=quiz_id, question_statement=question_statement, option1=option1,option2=option2,option3=option3,option4=option4, correct_option=correct_option)
                questions.append(new_question)
                db.session.add(new_question)
            db.session.commit()
            return {'message': 'Questions created successfully', 'ids': [question.id for question in questions]}, 201
        else:
            quiz_id = data.get('quiz_id')
            question_statement = data.get('question_statement')
            options = question_data.get('options')
            option1 = options[0]
            option2 = options[1]
            option3 = options[2]
            option4 = options[3]
            correct_option = question_data.get('correct_option')

            if not quiz_id or not question_statement or not options or not correct_option:
                return {'message': 'Missing required fields'}, 400

            new_question = Question(quiz_id=quiz_id, question_statement=question_statement, option1=option1,option2=option2,option3=option3,option4=option4, correct_option=correct_option)
            db.session.add(new_question)
            db.session.commit()

            return {'message': 'Question created successfully', 'id': new_question.id}, 201

    @swag_from('docs/question_patch.yml')
    def patch(self, id):
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        question = Question.query.filter_by(id=id).first()
        if not question:
            return {'message': 'Question not found'}, 404

        quiz_id = data.get('quiz_id')
        question_statement = data.get('question_statement')
        options = data.get('options')
        correct_option = data.get('correct_option')

        if quiz_id:
            question.quiz_id = quiz_id
        if question_statement:
            question.question_statement = question_statement
        if options:
            question.options = options
        if correct_option:
            question.correct_option = correct_option

        db.session.commit()
        return {'message': 'Question updated successfully'}, 200

    @swag_from('docs/question_delete.yml')
    def delete(self, id):
        question = Question.query.filter_by(id=id).first()
        if question:
            db.session.delete(question)
            db.session.commit()
            return {'message': 'Success'}, 200
        else:
            return {'message': 'Question not found'}, 404

api.add_resource(UserResource, "/api/v1/user", "/api/v1/user/<int:id>")
api.add_resource(SubjectResource, "/api/v1/subject", "/api/v1/subject/<int:id>")
api.add_resource(ChapterResource, "/api/v1/chapter", "/api/v1/chapter/<int:id>")
api.add_resource(QuizResource, "/api/v1/quiz", "/api/v1/quiz/<int:id>")
api.add_resource(QuestionResource, "/api/v1/question", "/api/v1/question/<int:id>")

