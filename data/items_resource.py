import flask
from flask import Flask, jsonify
from flask_restful import abort, Api, Resource
from data import db_session
from data.items import Item

blueprint = flask.Blueprint(
    'items_resource',
    __name__,
    template_folder='templates'
)


def abort_if_news_not_found(user_id):
    session = db_session.create_session()
    news = session.query(Item).get(user_id)
    if not news:
        abort(404, message=f"Item {user_id} not found")


@blueprint.route('/api/jobs/<int:items_id>')
def get_item(items_id):
    abort_if_news_not_found(items_id)
    db_sess = db_session.create_session()
    items = db_sess.query(Item).get(items_id)
    return jsonify({'items':
                        items.to_dict(only=('id', 'name',
                                            'description', 'price', 'quantity'))})


@blueprint.route('/api/items/')
def get_items():
    db_sess = db_session.create_session()
    items = db_sess.query(Item).all()
    return jsonify(
        {
            'items':
                [item.to_dict(only=('id', 'name',
                                    'description', 'price', 'quantity')) for item in items]
        }
    )
