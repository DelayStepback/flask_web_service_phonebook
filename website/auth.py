from flask import Blueprint, render_template, request, flash, redirect, url_for
from website.models import User, Client
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


#login
@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':

        # role
        # fake admin
        # from website.db_init import db
        # new_user = User(login='admin1', password=generate_password_hash('123', method='sha256'))
        # new_user.grant_permission('admin')
        # db.session.add(new_user)
        # db.session.commit()



        login = request.form.get('login')
        password = request.form.get('password')

        user = User.query.filter_by(login=login).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Вы успешно вошли в систему', category='success')
                login_user(user, remember=True) #remembering user fact logined
                return redirect(url_for('views.home'))
            else:
                flash('Пароль введен неверно, попробуйте снова', category='error')
        else:
            flash('Такого логина не существует', category='error')
    return render_template("login.html", user=current_user)

#logout
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

#sigh up

# CHECK IT
@auth.route('/sign-up', methods = ['GET', 'POST'])
@login_required
def sign_up():
    if request.method == 'GET':
         if current_user.has_permission('admin'):
             users = User.query.all()
             return render_template("sign_up.html", users_base_exist = User.query.all() != [], users=users, user=current_user)
    else:
        logout_user()
        return redirect(url_for('auth.login'))


#user search
@auth.route('/search-User', methods = ['POST', 'GET'])
@login_required
def search_User():
    if request.method == 'GET':
        return render_template("search_user.html", user=current_user)
    elif request.method == 'POST':

        number = request.form.get('search_by_number')
        if (len(str(number))) >= 5:
            clients = Client.query.filter(Client.number.startswith(number))
            number = False
            return render_template("search_user.html", clients=clients, user=current_user)
        else:
            flash('Номер должен быть от 5ти цифр', category='error')
            return render_template("search_user.html", user=current_user)
