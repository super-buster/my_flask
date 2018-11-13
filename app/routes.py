from . import app
from flask import render_template,Flask,redirect,session,url_for,flash,request
from app.forms import LoginForm
from app.models import User
from flask_login import current_user,login_user,logout_user,login_required
from werkzeug.urls import  url_parse
@app.route('/')
@app.route('/index')
def index():
    posts = [
        {
            'author': {'username': 'Haruhi'},
            'body': 'find something interesting!'
        }
    ]
    return render_template('index.html', title='Home page',  posts=posts)

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=LoginForm()
    if form.validate_on_submit():
        #查找数据库里面的符合条件的第一个对象
        user=User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        #记为登录状态
        login_user(user,remember=form.remember_me.data)
        next_page=request.args.get('next')
        #检查netloc属性是否被设置,确保安全
        if not next_page or url_parse(next_page).netloc!='':
            next_page=url_for('index')
        return redirect(next_page)
    return render_template('login.html',title='Sign in',form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed'