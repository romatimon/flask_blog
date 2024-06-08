from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user
import sqlalchemy as sa
from app import app
from app import db
from app.forms import LoginForm
from app.models import User


@app.route('/')
@app.route('/index')
def index():
    """Функция представления главной страницы."""
    user = {'username': 'Roman'}
    posts = [
        {
            'author': {'username': 'Ivan'},
            'body': 'Beautiful day in Moscow!'
        },
        {
            'author': {'username': 'Stepan'},
            'body': 'The Fallout movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Функция представления формы авторизации."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():  # validate_on_submit - проверяет и собирает данные из формы
        user = db.session.scalar(sa.select(User).where(
            User.username == form.username.data))  # scalar - возвращает первое значение первой строки результата
        if user is None or not user.check_password(form.password.data):  # проверка, что пароль действителен либо нет
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)  # функция регистрирует пользователя как вошедшего в
        # систему, а это означает, что для всех будущих страниц, на которые пользователь перейдет, будет задана
        # переменная current_user для этого пользователя
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
