from flask import Flask, render_template, make_response, jsonify, url_for
from flask_login import current_user, LoginManager, logout_user, login_required, login_user
from werkzeug.utils import redirect
from werkzeug.exceptions import abort
from data import db_session, items_resource
from werkzeug.security import generate_password_hash
from data.orders import Orders, OrderForm
from data.users import User, LoginForm, RegisterForm, ProfForm
from data.items import Item, ItemsForm
import os
from waitress import serve
from flask_ngrok import run_with_ngrok
from data.sent_email import send_email_order

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Weslia'
run_with_ngrok(app)
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/info.db")
db_sess = db_session.create_session()


@app.route('/')
def base():  # главная страничка
    items = db_sess.query(Item).all()
    return render_template('main.html', title='Главная', item_list=items,
                           css=url_for('static', filename='css/main.css'))


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():  # авторизация
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reg():  # регистрация
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User()
        new_user.email = form.email.data
        new_user.hashed_password = generate_password_hash(form.password.data)
        new_user.surname = form.surname.data
        new_user.name = form.name.data
        new_user.age = form.age.data
        new_user.address = form.address.data
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            return render_template('register.html',
                                   message="Существует уже аккаунт",
                                   form=form)
        db_sess.add(new_user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация',
                           form=form)


@app.route('/item_add', methods=['GET', 'POST'])
@login_required
def add_item():  # добавление товара
    if not current_user.moder:
        return redirect('/')
    form = ItemsForm()
    if form.validate_on_submit():
        item = Item()
        item.name = form.name.data
        item.description = form.description.data
        item.price = form.price.data
        item.img = form.img.data
        item.quantity = form.quantity.data
        db_sess.add(item)
        db_sess.commit()
        return redirect('/')
    return render_template('items.html', title='Добавление Товара',
                           form=form)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_jobs(id):  # удаление товара
    a = db_sess.query(Item).get(id)
    if not a:
        abort(404)
        return
    if not current_user.moder:
        return redirect('/')
    db_sess.delete(a)
    db_sess.commit()
    return redirect('/')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):  # редактирование товара
    form = ItemsForm()
    a = db_sess.query(Item).get(id)
    if not a:
        return redirect('/')
    if not current_user.moder:
        return redirect('/')
    if form.validate_on_submit():
        a.name = form.name.data
        a.description = form.description.data
        a.price = form.price.data
        a.quantity = form.quantity.data
        a.img = form.img.data
        db_sess.commit()
        return redirect('/')
    return render_template('items_edit.html', title='Редактирование Товара',
                           form=form, lol=a)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():  # редактирование профиля
    if current_user.moder:
        return redirect('/')
    form = ProfForm()
    user = db_sess.query(User).get(current_user.id)
    if form.validate_on_submit():
        user.email = form.email.data
        user.surname = form.surname.data
        user.name = form.name.data
        user.age = form.age.data
        user.address = form.address.data
        db_sess.commit()
        return render_template('profile.html', title='Профиль', form=form, u=user)
    return render_template('profile.html', title='Профиль', form=form, u=user)


@app.route('/buy/<int:id>', methods=['GET', 'POST'])
@login_required
def make_order(id):  # создание заказа
    form = OrderForm()
    a = db_sess.query(Item).get(id)
    if form.validate_on_submit():
        ords = Orders()
        ords.quantity = form.quantity.data
        ords.buy = id
        ords.buyer = current_user.id
        if a.quantity - ords.quantity < 0:
            abort(404)
            return
        db_sess.add(ords)
        a.quantity = a.quantity - ords.quantity
        db_sess.commit()
        send_email_order(current_user.email, ords.id, ords.item.name,
                         ords.item.description, ords.item.quantity * ords.item.price,
                         img=f'static\img\{ords.item.img}')
        return redirect('/')
    return render_template('New_order.html', title='Оформление', item=a,
                           form=form)


@app.route('/orders', methods=['GET'])
@login_required
def view_orders():  # просмотр заказов
    a = list(current_user.orders)
    return render_template('view_orders.html', title='Заказы', item_list=a)


@app.route('/admin_orders', methods=['GET', 'POST'])
@login_required
def admin_orders():  # просмотр заказов администратором
    if not current_user.moder:
        return redirect('/')
    a = db_sess.query(Orders).all()
    return render_template('admin_ord.html', title='Заказы', item_list=a)


@app.route('/edit_status/<int:id>/<int:st>', methods=['GET', 'POST'])
@login_required
def edit_status(id, st):  # редактирование статусов заказов
    if not current_user.moder:
        return redirect('/')
    a = db_sess.query(Orders).get(id)
    if not a:
        abort(404)
        return
    if st not in [1, 2, 3, 4]:
        abort(404)
        return
    if st == 1:
        a.condition = "Не оплачено"
        a.paid_for = 0
    else:
        a.paid_for = 1
        if st == 2:
            a.condition = "Оформление заказа"
        elif st == 3:
            a.condition = "Доставка"
        elif st == 4:
            a.condition = "Доставлено"
    db_sess.commit()
    return redirect('/admin_orders')


@app.route('/delete_order/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_order(id):  # удаление заказов
    if not current_user.moder:
        return redirect('/')
    a = db_sess.query(Orders).get(id)
    if not a:
        abort(404)
        return
    a.item.quantity = a.item.quantity + a.quantity
    db_sess.delete(a)
    db_sess.commit()
    return redirect('/admin_orders')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'error'}), 404)


if __name__ == '__main__':
    app.register_blueprint(items_resource.blueprint)
    port = int(os.environ.get("PORT", 5000))
    # serve(app, host='0.0.0.0', port=5000)
    app.run()
