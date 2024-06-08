from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    """Форма входа пользователя в систему."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Форма регистрации пользователя."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Метод проверяет, существует ли в базе данных пользователь с указанным именем
        пользователя, и сохраняет этого пользователя в переменной user."""
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """Метод проверяет, существует ли в базе данных пользователь с указанным email,
         и сохраняет этого пользователя в переменной user."""
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    """Форма редактирования профиля."""
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=150)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """Метод проверяет имя пользователя в форме редактирования профиля.
        Если имя пользователя, введенное в форму, совпадает с исходным именем пользователя,
        то нет причин проверять базу данных на наличие дубликатов."""
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == self.username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')

