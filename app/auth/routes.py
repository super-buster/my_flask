from flask import render_template,Flask,redirect,session,url_for,flash,request
from werkzeug.urls import  url_parse
from flask_login import current_user,login_user,logout_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm,ResetPasswordRequestForm,RestPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email

@bp.route('/login',methods=['GET','POST'])
def login():
    #先确保没有登录
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form=LoginForm()
    if form.validate_on_submit():
        #查找数据库里面的符合条件的第一个对象
        user=User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        #记为登录状态
        login_user(user,remember=form.remember_me.data)
        next_page=request.args.get('next')
        #检查netloc属性是否被设置,确保安全
        if not next_page or url_parse(next_page).netloc!='':
            next_page=url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html',title='Sign in',form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash(_('You have been logged out.'))
    return redirect(url_for('main.index'))

@bp.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,
                  username=form.username.data,
                  password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('You can now login.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',title='Register' ,form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)

@bp.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user=User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form= RestPasswordForm()
    if form.validate_on_submit():
        user.password=form.password.data
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)