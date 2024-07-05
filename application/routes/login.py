from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from application.models import Users, app

login_bp = Blueprint('login_bp', __name__)


def check_name_password(name, password):
    with app.app_context():
        users = Users.query.all()
    for user in users:
        if user.username == name and user.password == password:
            return True
    else:
        return False


@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            if check_name_password(username, password):
                flash("登录成功：用户{}".format(username))
                return redirect(url_for('index.index'))
            else:
                flash('用户名不存在或密码错误！')
                return redirect(url_for('login_bp.login'))
        else:
            flash('请输入用户名和密码！')
            return redirect(url_for('login_bp.login'))

    return render_template('login.html')
