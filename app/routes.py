from . import app
from . import db
from flask import render_template,Flask,redirect,session,url_for,flash,request,abort
from app.forms import LoginForm, RegistrationForm , EditProfileForm
from app.models import User
from flask_login import current_user,login_user,logout_user,login_required
from werkzeug.urls import  url_parse
from datetime import datetime
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
    #先确保没有登录
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

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,
                  username=form.username.data,
                  password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register' ,form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user=User.query.filter_by(username=username).first()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    if user is None:
        abort(404)
    return render_template('user.html',user=user,posts=posts)

@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form=EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('You changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method  == 'GET':
        form.username.data=current_user.username
        form.about_me.data=current_user.about_me
    return render_template('edit_profile.html',title='Edit Profile',form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} is not found.'.format(username))
        return redirect(url_for('index'))
    if user==current_user:
        flash('You can not follow yourself!')
        return redirect(url_for('user',username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user',username=username))

@app.route('/unfollow/<username>')
@app.login_required
def unfollow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user==current_user:
        flash('You cannot unfollow youself!')
        return redirect(url_for('user',username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user',username=username))

#动态获取用户登录的最后时间
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen=datetime.utcnow()
        db.session.commit()

@app.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed'