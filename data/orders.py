import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class Orders(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'order'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    buy = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("item.id"), index=True)
    buyer = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"), index=True)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=1)
    condition = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='Не оплачено')
    paid_for = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=0)
    user = orm.relation('User', back_populates='orders')
    item = orm.relation('Item')

    def __repr__(self):
        return f'{self.id}'


class OrderForm(FlaskForm, SerializerMixin):
    quantity = IntegerField('Количество')
    submit = SubmitField('Оформить')
