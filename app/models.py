from hashlib import md5

import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from flask_login import UserMixin
from app import login

# hashlib/md5 - модуль для создания хеша по алгоритму MD5

# Optional - объявляет, что переменная имеет тип, например, str, но это является «необязательным», что означает,
# что она также может быть None

# UserMixin - миксин, который позволяет нам использовать как is_authenticated(), is_active(), is_anonymous() и get_id()

# WriteOnlyMapped - тип связи, который добавляет метод select(), возвращающий запрос к
# базе данных для связанных элементов

# relationship - функция, для установки отношений между моделями

# back_populates - аргумент, ссылается на имя атрибута отношения на другой стороне

# Связь, в которой экземпляры класса связаны с другими экземплярами того же класса, называется самореферентной связью


"""Ассоциативная таблица подписчиков."""
followers = sa.Table(
    'followers',
    db.metadata,  # метаданные, это место, где SQLAlchemy хранит информацию обо всех таблицах в базе данных
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),  # составной первичный ключ
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)  # составной первичный ключ
)


class User(UserMixin, db.Model):
    """Модель таблицы БД пользователей."""
    id: so.Mapped[int] = so.mapped_column(primary_key=True)  # первичный ключ
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: so.WriteOnlyMapped['User'] = so.relationship(  # подписчики
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')

    # Это отношение связывает экземпляры User с другими экземплярами User, поэтому в качестве соглашения предположим,
    # что для пары пользователей, связанных этим отношением, левый пользователь следит за правым пользователем. Я
    # определяю связь так, как ее видит пользователь с левой стороны, с именем following, потому что когда я
    # запрашиваю эту связь с левой стороны, я получаю список пользователей, на которых подписывается пользователь с
    # левой стороны. И наоборот, followers связь начинается с правой стороны и находит всех пользователей,
    # которые подписаны на данного пользователя.

    # secondary - настраивает таблицу ассоциаций, которая используется для этой связи с followers.

    # primaryjoin - указывает условие, которое связывает объект с ассоциативной таблицей. В связи following
    # пользователь должен соответствовать атрибуту follower_id ассоциативной таблицы, поэтому условие отражает это.
    # Выражение followers.c.follower_id ссылается на столбец follower_id ассоциативной таблицы. В отношениях
    # followers роли поменялись местами, поэтому пользователь должен соответствовать столбцу followed_id.

    # secondaryjoin - указывает условие, которое связывает ассоциативную таблицу с пользователем на другой стороне
    # связи. В отношениях following пользователь должен соответствовать столбцу followed_id, а в отношениях followers
    # пользователь должен соответствовать столбцу follower_id.

    def __repr__(self):
        return '<User> {}'.format(self.username)

    def avatar(self, size):
        """Метод возвращает URL изображения аватара пользователя,
        масштабированный до требуемого размера в пикселях."""
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

        # digest = md5('rtimonin569@gmail.com'.encode('utf-8')).hexdigest()
        # return f'https://www.gravatar.com/avatar/{digest}'

    def set_password(self, password):
        """Метод генерирует хэш при создании пароля."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Метод проверяет, совпадает ли хэш сгенерированный ранее."""
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        """Метод подлиски и проверкой, что подписки не было ранее."""
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        """Метод отписки и проверки, что подписка существовала ранее."""
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        """Метод проверяет, подписан ли текущий пользователь на другого пользователя."""
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        """Метод возвращает количество подписчиков пользователя."""
        query = sa.select(sa.func.count()).select_from(self.followers.select().subquery())
        return db.session.scalar(query)

    # select_from() определяет таблицу, что помогает свободно формировать запросы

    # subquery() всякий раз, когда запрос включается как часть более крупного запроса, SQLAlchemy требует
    # преобразования внутреннего запроса в подзапрос путем вызова метода subquery

    def following_count(self):
        """Метод возвращает количество подписок пользователя."""
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)

    def following_posts(self):
        """Метод запроса на подписанные публикации."""
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )


@login.user_loader
def load_user(id):
    """Метод загрузки пользователя из БД с заданным идентификатором."""
    return db.session.get(User, int(id))


class Post(db.Model):
    """Модель таблицы БД записей (постов)."""
    id: so.Mapped[int] = so.mapped_column(primary_key=True)  # первичный ключ
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),  # внешни ключ для user.id
                                               index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
