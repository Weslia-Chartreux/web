import datetime
import sqlalchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from wtforms import StringField, TextAreaField, PasswordField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'user'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True, index=True)
    moder = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=0)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True)
    orders = orm.relation("Orders", back_populates='user')

    def __repr__(self):
        return self.name

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class LoginForm(FlaskForm, SerializerMixin):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm, SerializerMixin):
    surname = StringField('Фамилия')
    name = StringField('Имя')
    age = IntegerField("Возвраст")
    address = StringField("Место доставки")
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Применить')
