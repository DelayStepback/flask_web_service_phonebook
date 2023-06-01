from flask import Flask
from flask_login import LoginManager
from website.db_init import db, DB_NAME
from website.models import Root #create_fake_users


def create_admin(login, password1):
    new_user = User(login=login, password=generate_password_hash(password1, method='sha256'))
    new_user.grant_permission('admin')
    db.session.add(new_user)
    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjsdfijsdfiji xcvzxkocv' # secret cookie key don't show to everybody


# postgresql://root:r4f1U-82Kiy-gQ0QN-nkXT5@212.193.61.16/database
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///..\instance\{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from website.views import views
    from website.auth import auth
    from website.database import database

    app.register_blueprint(views, url_prefix= '/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(database, url_prefix='/')

    from website.models import User


    with app.app_context():
        db.create_all()
        if Root.query.filter_by(location='root').first() == None:
            print('root created')
            root = Root()
            root.id = 0
            root.id_parent = -1
            root.location = 'root'
            db.session.add(root)
            db.session.commit()

            # # create admin
            # create_admin('admin', 'qwer12')


    # конструкция говорит фласку, как мы загружаем юзеров
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

from flask import request, flash, url_for, redirect
from werkzeug.security import generate_password_hash

from website.models import User, Client
app = create_app()

# user logic
@app.route('/add_user/', methods=['POST'])
def insert_user():
    if request.method == "POST":
        login = request.form.get('login')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        # valid information
        user = User.query.filter_by(login=login).first()

        if user:
            flash('Такой логин уже существует', category='error')
            return redirect(url_for('auth.sign_up'))

        if len(login) < 4:
            flash('Логин должен быть длиннее 4-х символов', category='error')
        elif password1 != password2:
            flash('Пароли не совпадают', category='error')
        elif len(password1) < 6:
            flash('Пароль должен быть длиннее 6-ти символов', category='error')
        else:
            new_user = User(login=login, password=generate_password_hash(password1, method='sha256'))
            if request.form.get('RadiosUser') == 'admin':
                new_user.grant_permission('admin')
            else:
                new_user.grant_permission('user')
            db.session.add(new_user)
            db.session.commit()

            # login_user(user, remember=True)  # remembering user fact logined
            flash('Аккаунт создан', category='success')
            return redirect(url_for('auth.sign_up'))
        return redirect(url_for('auth.sign_up'))

@app.route('/update_user/', methods=['POST'])
def update_user():
    if request.method == "POST":
        my_data = User.query.get(request.form.get('id'))

        my_data.login = request.form['login_user']
        password = request.form['password_user']
        #role
        my_data.password = generate_password_hash(password, method='sha256')

        db.session.commit()
        flash("Аккаунт обновлен")
        return redirect(url_for('auth.sign_up'))

@app.route('/delete_user/<id>/', methods=['GET', 'POST'])
def delete_user(id):
    my_data = User.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Аккаунт удален")
    return redirect(url_for('auth.sign_up'))

# client logic
@app.route('/add/', methods=['POST'])
def insert_client():
    if request.method == "POST":

        royalty_get = request.form.get('inlineRadioOptions')
        if royalty_get == "option1":
            royalty_get = 0
        elif royalty_get == "option2":
            royalty_get = 1 # middle
        else:
            royalty_get = 2 # good
        id_root = request.form.get('location_client')

        #create_fake_users(5000, id_root)

        client = Client(
            name=request.form.get('name_client'),
            number=request.form.get('number_client'),
            role=request.form.get('role_client'),
            royalty=royalty_get
        )
        client.grant_root(id_root)
        db.session.add(client)
        db.session.commit()
        flash("Client added successfully")
        return redirect(url_for('database.datebase_Add', location_id=id_root, curr_page=1))
@app.route('/update/', methods=['POST'])
def update():
    if request.method == "POST":
        my_data = Client.query.get(request.form.get('id'))

        royalty_get = request.form.get('inlineRadioOptions2')
        if royalty_get == "option1":
            royalty_get = 0
        elif royalty_get == "option2":
            royalty_get = 1  # middle
        else:
            royalty_get = 2  # good

        my_data.name = request.form['name_client']
        my_data.number = request.form['number_client']
        my_data.role = request.form['role_client']
        my_data.royalty = royalty_get

        db.session.commit()
        flash("Данные обновлены")

        # to repair
        return redirect(url_for('database.datebase_Add', location_id=0, curr_page=1))

@app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    my_data = Client.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Данные удалены")
    return redirect(url_for('database.datebase_Add', location_id=0, curr_page=1))

# root logic
@app.route('/add_root/', methods=['POST'])
def insert_root():
    if request.method == "POST":
        location = request.form.get('name_root')
        location_id_parent = request.form.get('location_root')

        # valid information
        root = Root.query.filter_by(location = location, id_parent = location_id_parent).first()
        if root:
            flash('Такая папка в этой директории уже существует', category='error')
            return redirect(url_for('database.datebase_Add', location_id=0, curr_page=1))

        new_root = Root(location=location, id_parent = location_id_parent)
        db.session.add(new_root)
        db.session.commit()

        # login_user(user, remember=True)  # remembering user fact logined
        flash('Каталог создан', category='success')
        return redirect(url_for('database.datebase_Add', location_id=new_root.id, curr_page=1))

@app.route('/update_root/<root_id>', methods=['POST'])
def update_root(root_id):
    if request.method == "POST":
        my_data = Root.query.get(root_id)

        my_data.location = request.form['location_name']

        db.session.commit()
        flash("Catalog is updated")

        return redirect(url_for('database.datebase_Add', location_id=int(root_id), curr_page=1))


# ВНИМАНИЕ удаление всех вложенных в этот каталог клиентов и КАТАЛОГОВ

def root_Del_rec(root_id):
    roots_to_del = Root.query.filter(Root.id_parent == root_id) # ищем детей нашего рута
    for root_to_del in roots_to_del:


        clients_of_root = Client.query.filter(Client.roots.any(id=int(root_to_del.id)))
        for client in clients_of_root:
            db.session.delete(client)  # удаляем клиентов, привязанных к root_id

        root_Del_rec(root_to_del.id)  # рекурсивно вниз по папкам
        db.session.delete(root_to_del)


@app.route('/delete_root/<root_id>', methods=['POST'])
def delete_root(root_id):
    if request.method == "POST":

        my_data = Root.query.get(root_id)
        parent_save_to_link = my_data.id_parent

        clients_of_root = Client.query.filter(Client.roots.any(id = int(root_id)))
        for client in clients_of_root:
            db.session.delete(client)  # удаляем клиентов, привязанных к root_id

        root_Del_rec(root_id) # рекурсивно вниз по папкам
        db.session.delete(my_data)

        db.session.commit()
        flash("Каталог и все вложенные в него удалены")

        return redirect(url_for('database.datebase_Add', location_id=parent_save_to_link, curr_page=1))




if __name__ == '__main__':

    app.run(debug=True)





















