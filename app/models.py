from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login
from hashlib import md5
from flask import request



class User(UserMixin,db.Model):
    __tablename__= 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me=db.Column(db.Text())
    last_seen=db.Column(db.DateTime(),default=datetime.utcnow)
    #一对多的关系：dynamic (不加载记录,但提供加载记录的查询)
    posts=db.relationship('Post',backref='author',lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    #验证密码
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def gravatar(self,size=648,default='identicon',rating='g'):
        url='http://www.gravatar.com/avatar'
        hash=md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url,hash=hash,size=size,default=default,rating=rating        )


    def __repr__(self):
        return '<User {}>'.format(self.username)

class Post(db.Model):
    __tablename__='post'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.String(140))
    timestamp=db.Column(db.DateTime, index=True, default=datetime.utcnow)
    #多的一方通过外键关联到user表
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self):
        return '<Post {}'.format(self.body)

#用户加载函数
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
