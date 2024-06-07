from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


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
    form = LoginForm()
    if form.validate_on_submit():  # запускается проверка данных из формы
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))  # flash, сообщение для пользователя при успешной отправке
        # данных формы
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
