from hashlib import md5
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


class User(UserMixin, db.Model):
    """Модель таблицы БД пользователей."""
    id: so.Mapped[int] = so.mapped_column(primary_key=True)  # первичный ключ
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')

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
    id: so.Mapped[int] = so.mapped_column(primary_key=True)  # первичный ключ
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),  # внешни ключ для user.id
                                               index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
