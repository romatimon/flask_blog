from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit  # парсит URL-адрес на пять компонентов пути
import sqlalchemy as sa
from app import app
from app import db
from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.route('/')
@app.route('/index')
@login_required  # декоратор не разрешает доступ пользователям, которые не прошли проверку подлинности
def index():
    """Функция представления главной страницы."""
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
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Функция представления формы авторизации."""
    if current_user.is_authenticated:  # если пользователь авторизован, это свойство возвращает истину
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
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    """Функция выхода из системы."""
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Функция просмотра регистрации пользователя."""
    if current_user.is_authenticated:  # если пользователь авторизован, это свойство возвращает истину
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():  # validate_on_submit - проверяет и собирает данные из формы
        user = User(username=form.username.data, email=form.email.data)  # создает экземпляр нового пользователя
        user.set_password(form.password.data)  # с помощью метода создает пароль
        db.session.add(user)  # добавляет данные в БД
        db.session.commit()  # сохраняет данные в БД
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))  # перенаправляет на приглашение для входа
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')  # динамический компонент
@login_required
def user(username):
    """Функция просмотра профиля пользователя."""
    user = db.first_or_404(sa.select(User).where(
        User.username == username))  # возвращает первый результат запроса или ошибку 404, если в нем нет строк.
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)