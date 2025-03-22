from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField, DateField, SelectField, RadioField
from wtforms.validators import Length, Email, EqualTo, DataRequired, ValidationError
from models.models import User, Subject, Chapter, Quiz
from wtforms.fields import TimeField

class RegistrationFrom(FlaskForm):
    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email alreadty exist! try different email address')
    email_address = StringField(label='Email', validators=[Email(), DataRequired()])
    full_name = StringField(label='Full Name', validators=[Length(min=3, max=20),DataRequired()])
    qualification = StringField(label='Qualification', validators=[Length(max=10)])
    dob = DateField(label='DOB')
    password1 = PasswordField(label='Password:', validators=[Length(min=4), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    email_address = StringField(label='Email Address:', validators=[Email(),DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Login')


class AddSubjectForm(FlaskForm):
    subject_name = StringField(label='Subject Name', validators=[DataRequired()])
    description = StringField(label='Description',validators=[Length(max=100)])
    submit = SubmitField(label='Add Subject')

class AddChapterForm(FlaskForm):
    chapter_name = StringField(label='Chapter', validators=[DataRequired()])
    description = StringField(label='description',validators=[Length(max=50)])
    subject_id = SelectField(label=' Select Subject',choices=[], validators=[DataRequired()])
    submit = SubmitField(label='Add Chapter')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject_id.choices = [(subject.id, subject.name) for subject in Subject.query.all()]

class AddQuizForm(FlaskForm):
    chapter_id = SelectField(label='Select Chapter', choices=[], validators=[DataRequired()])
    title = StringField(label='Quiz Title')
    date_of_quiz = DateField(label='Select Date of Quiz')
    time_duration = TimeField(label='Duration (HH:MM)', validators=[DataRequired()], format='%H:%M')
    remark = StringField(label='Remark', validators=[Length(max=200)])
    submit = SubmitField(label='Add Quiz')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chapter_id.choices = [(chapter.id, chapter.name) for chapter in Chapter.query.all()]


class AddQuestionForm(FlaskForm):
    quiz_id = SelectField(label='Select Quiz', choices=[],validators=[DataRequired()])
    question_statement = StringField(label='Question Satement', validators=[DataRequired()])
    option1 = StringField(label='Option1')
    option2 = StringField(label='Option2')
    option3 = StringField(label='Option3')
    option4 = StringField(label='Option4')

    correct_option = StringField(label='Correct option', validators=[DataRequired()])
    submit = SubmitField(label='Add Question')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quiz_id.choices = [(quiz.id, quiz.title) for quiz in Quiz.query.all()]


class QuizAttemptForm(FlaskForm):
    selected_option = RadioField("Choose an answer", choices=[], coerce=str)
    next = SubmitField("Next")
    prev = SubmitField("Previous")
    submit = SubmitField("Submit")