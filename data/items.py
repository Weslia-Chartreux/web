import sqlalchemy
from flask_wtf import FlaskForm
from sqlalchemy_serializer import SerializerMixin
from wtforms import StringField, FloatField, SubmitField, IntegerField

from .db_session import SqlAlchemyBase


class Item(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'item'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    img = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        return f'{self.name}'


class ItemsForm(FlaskForm, SerializerMixin):
    name = StringField('Название')
    description = StringField("Описание")
    price = FloatField("Цена")
    quantity = IntegerField("Количество на складе")
    img = StringField("Картинка")
    submit = SubmitField('Применить')
