# _*_coding:utf-8_*_
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm
from .. import db
from datetime import datetime


@auth.before_app_request  # 程序会在每次请求前运行
def before_request():     # 这个跟main文件夹中的errors.py类似，都是注册到auth（main）蓝图上的，但是因为
                            # app_errorhandlerh和before_app_request都加了app，所以会“共享”给整个app“使用”
    if current_user.is_authenticated:  # 方法已经变成了属性，后面再回头看
        current_user.ping()  # 不知道ping(current_user)可行不


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # user = User.query.filter_by(email=form.email.data).first()
        # if user is not None and user.verify_password(form.password.data):
        #     login_user(user, form.remember_me.data)
        flash("now logged in.")
        return redirect(request.args.get('next') or url_for('main.index'))
        # #login_user后current_user发生改变
        # #传入main.index改变页面显示
        # flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)
    # 为什么main/views.py中没有在前面加main/,学完这几章再回头看


@auth.route('/logout')
@login_required  # 表示登录认证过的用户才能访问这个路由
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        # 从而得到password_hash的值
        # password=的形式会自动调用@property装饰的password方法
        db.session.add(user)
        flash('You can now login.')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)
