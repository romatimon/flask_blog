from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import app
from app import db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from app.models import User, Post


# urllib.parse/urlsplit - делит/парсит URL-адрес на пять компонентов пути

# login_required - декоратор не разрешает доступ пользователям, которые не прошли проверку подлинности
# before_request - декоратор запускается перед каждым запросом к экземпляру приложения

# scalar - возвращает первое значение первой строки результата или None если результатов нет
# first_or_404 - возвращает первый результат запроса или ошибку 404, если в нем нет строк

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """Функция представления главной страницы."""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = db.session.scalars(current_user.following_posts()).all()
    return render_template("index.html", title='Home Page', form=form,
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Функция представления формы авторизации."""
    if current_user.is_authenticated:  # если пользователь авторизован, это свойство возвращает истину
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():  # validate_on_submit - проверяет и собирает данные из формы
        user = db.session.scalar(sa.select(User).where(
            User.username == form.username.data))
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
        User.username == username))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)


@app.before_request
def before_request():
    """Функция проверяет, соответствует ли current_user пользователю вошедшему в систему,
    и в этом случае в поле last_seen устанавливается текущее время."""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Функция редактирования профиля."""
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    """Функция маршрута для добавления подписки."""
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    """Функция маршрута для отмены подписки."""
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/explore')
@login_required
def explore():
    """Функция просмотра всех сообщений."""
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.session.scalars(query).all()
    return render_template('index.html', title='Explore', posts=posts)