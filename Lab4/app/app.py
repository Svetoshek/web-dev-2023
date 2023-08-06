
from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user, login_required
import mysql.connector
from modules.validation import checkLogin, checkPassword, checkLastName, checkFirstName
from mysql_db import MySQL

PERMITED_PARAMS = ['login', 'password', 'last_name',
                   'first_name', 'middle_name', 'role_id']
EDIT_PARAMS = ['last_name', 'first_name', 'middle_name', 'role_id']

MESSAGE_CHECK_FIELDS = 'Проверьте, пожалуйста, корректность введенных данных.'

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

db = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице нужно авторизироваться.'
login_manager.login_message_category = 'warning'


class User(UserMixin):

    def __init__(self, user_id, user_login):
        self.id = user_id
        self.login = user_login


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        print(f'При аутентифкации пароль {password}')
        remember = request.form.get('remember_me') == 'on'

        query = 'SELECT * FROM users WHERE login = %s and password_hash = SHA2(%s, 256);'
        user = False  
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query, (login, password))
            user = cursor.fetchone()
        if user:
            login_user(User(user.id, user.login), remember=remember)
            flash('Вы успешно прошли аутентификацию!', 'success')
            param_url = request.args.get('next')
            return redirect(param_url or url_for('index'))
        flash('Введён неправильный логин или пароль.', 'danger')
    return render_template('login.html')


@app.route('/users')
def users():
    query = ('SELECT users.*, roles.name AS role_name FROM users '
             'LEFT JOIN roles ON roles.id = users.role_id')
    with db.connection().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        users_list = cursor.fetchall()

    return render_template('users/index.html', users_list=users_list)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():


    error_list = {}

    if request.method == 'GET':
        return render_template('users/change_password.html', error_list=error_list)

    current_password = request.form.get('oldPassword') or None
    new_password = request.form.get('newPassword') or None
    new_password2 = request.form.get('newPassword2') or None

    if checkPassword(current_password):
        error_list['current_password'] = checkPassword(current_password)
    if checkPassword(new_password):
        error_list['new_password'] = checkPassword(new_password)
    if checkPassword(new_password2):
        error_list['new_password2'] = checkPassword(new_password2)
    if error_list:
        flash('Проверьте введенные данные', 'danger')
        return render_template('users/change_password.html', error_list=error_list)

    with db.connection().cursor(named_tuple=True) as cursor:
        query = 'SELECT password_hash FROM users WHERE id=%s'
        cursor.execute(query, (current_user.id,))
        user = cursor.fetchone()

    with db.connection().cursor(named_tuple=True) as cursor:
        query = 'SELECT SHA2(%s, 256) as current_password;'
        cursor.execute(query, (current_password,))
        calculated_hash = cursor.fetchone().current_password

    if user:
        if user.password_hash == calculated_hash:
            if new_password == new_password2:
                query = (
                    'UPDATE users SET password_hash=SHA2(%(new_password)s, 256) WHERE id=%(id)s;')
                dict_for_query = {
                    'new_password': new_password,
                    'id': current_user.id,
                }
                try:
                    with db.connection().cursor(named_tuple=True) as cursor:
                        cursor.execute(query, dict_for_query)
                        db.connection().commit()
                        flash(
                            'Пароль успешно изменен', 'success')
                        return redirect(url_for('index'))
                except mysql.connector.errors.DatabaseError:
                    db.connection().rollback()
                    flash('Во время обновления пароля произошел сбой', 'danger')
                    return render_template('users/change_password.html', error_list=error_list)
            else:
                flash('Введенные пароли не совпадают', 'danger')
                error_list['new_password2'] = {'Пароли должны совпадать'}
                return render_template('users/change_password.html', error_list=error_list)
        else:
            flash('Текущий пароль не совпадает с паролем введенным в поле "Введите старый пароль"', 'danger')
            return render_template('users/change_password.html', error_list=error_list)
    return render_template('users/change_password.html', error_list=error_list)


@app.route('/users/new')
@login_required
def users_new():
    return render_template('users/new.html', roles_list=load_roles(), user={}, error_list={})


def load_roles():
    with db.connection().cursor(named_tuple=True) as cursor:
        query = 'SELECT * FROM roles;'
        cursor.execute(query)
        roles = cursor.fetchall()
    return roles


def extract_params(params_list):
    params_dict = {}
    for param in params_list:
        params_dict[param] = request.form.get(param) or None
    return params_dict


@app.route('/users/create', methods=['POST'])
@login_required
def create_user():

    error_list = {}

    params = extract_params(PERMITED_PARAMS)
    if checkLogin(params.get('login')):
        error_list['login'] = checkLogin(params.get('login'))
    if checkPassword(params.get('password')):
        error_list['password'] = checkPassword(params.get('password'))
    if checkLastName(params.get('last_name')):
        error_list['last_name'] = checkPassword(params.get('last_name'))
    if checkFirstName(params.get('first_name')):
        error_list['first_name'] = checkPassword(params.get('first_name'))
    if error_list:
        return render_template('users/new.html', user=params, roles_list=load_roles(), error_list=error_list)

    query = ('INSERT INTO users(login, password_hash, last_name, '
             'first_name, middle_name, role_id) '
             'VALUES ( %(login)s, SHA2(%(password)s, 256), '
             '%(last_name)s, %(first_name)s, %(middle_name)s, %(role_id)s);')
    try:
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query, params)
            db.connection().commit()
            flash(
                f"Успешно! Создан пользователь @{params.get('login')}", 'success')
    except mysql.connector.errors.DatabaseError as error:
        db.connection().rollback()
        flash(MESSAGE_CHECK_FIELDS, 'danger')

        return render_template('users/new.html', user=params, roles_list=load_roles(), error_list=error_list)

    return redirect(url_for('users'))



@ app.route('/users/<int:user_id>/update', methods=['POST'])
@ login_required
def update_user(user_id):
    params = extract_params(EDIT_PARAMS)
    params['id'] = user_id
    error_list = {}
    if checkLastName(params.get('last_name')):
        error_list['last_name'] = checkPassword(params.get('last_name'))
    if checkFirstName(params.get('first_name')):
        error_list['first_name'] = checkPassword(params.get('first_name'))
    if error_list:
        return render_template('users/edit.html', user=params, roles_list=load_roles(), error_list=error_list)

    query = ('UPDATE users SET last_name=%(last_name)s, first_name=%(first_name)s, '
             'middle_name=%(middle_name)s, role_id=%(role_id)s WHERE id=%(id)s;')
    try:
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query, params)
            db.connection().commit()
            flash('Успешно! Данные о пользователе были обновлены', 'success')
    except mysql.connector.errors.DatabaseError:
        db.connection().rollback()
        flash(MESSAGE_CHECK_FIELDS, 'danger')
        return render_template('users/edit.html', user=params, roles_list=load_roles(), error_list=error_list)

    return redirect(url_for('users'))


@ app.route('/users/<int:user_id>/edit')
@ login_required
def edit_user(user_id):
    query = 'SELECT * FROM users WHERE users.id = %s;'
    cursor = db.connection().cursor(named_tuple=True)
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return render_template('users/edit.html', user=user, roles_list=load_roles(), error_list={})


@ app.route('/users/<int:user_id>/delete', methods=['POST'])
@ login_required
def delete_user(user_id):
    query = 'DELETE FROM users WHERE users.id=%s;'
    try:
        cursor = db.connection().cursor(named_tuple=True)
        cursor.execute(query, (user_id,))
        db.connection().commit()
        cursor.close()
        flash('Пользователь успешно удален', 'success')
    except mysql.connector.errors.DatabaseError:
        db.connection().rollback()
        flash('При удалении пользователя возникла ошибка.', 'danger')
    return redirect(url_for('users'))


@ app.route('/user/<int:user_id>')
def show_user(user_id):
    query = ('SELECT users.*, roles.name AS role_name FROM users '
             'LEFT JOIN roles ON roles.id = users.role_id '
             'WHERE users.id = %s;')
    cursor = db.connection().cursor(named_tuple=True)
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return render_template('users/show.html', user=user)


@ app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@ login_manager.user_loader
def load_user(user_id):
    query = 'SELECT * FROM users WHERE users.id = %s;'
    cursor = db.connection().cursor(named_tuple=True)
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(user.id, user.login)
    return None


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/page_not_found.html', description=error), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return render_template('errors/method_not_allowed.html', description=error), 405
