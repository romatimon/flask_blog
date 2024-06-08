from hashlib import md5  # хеширование данных заданного файла по алгоритму MD5
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    """Модель таблицы БД пользователей."""
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')

    def __repr__(self):
        return '<User> {}'.format(self.username)

    def avatar(self, size):
        """Метод возвращает URL изображения аватара пользователя,
        масштабированный до требуемого размера в пикселях."""
        # digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        # return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

        digest = md5('rtimonin569@gmail.com'.encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}'

    def set_password(self, password):
        """Метод генерирует хэш при создании пароля."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Метод проверяет, совпадает ли хэш сгенерированный ранее."""
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    """Метод загрузки пользователя из БД с заданным идентификатором."""
    return db.session.get(User, int(id))


class Post(db.Model):
    """Модель таблицы БД записей (постов)."""
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
