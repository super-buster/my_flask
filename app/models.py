# -*- coding: utf-8 -*-
from datetime import datetime
from app import db ,login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin , LoginManager
from . import login
from hashlib import md5
from time import time
from flask import current_app
from markdown import markdown
import bleach
import jwt

class Permission:
    FOLLOW=0x01
    COMMENT=0x02
    WRITE_ARTICLES=0x04
    MODERATE_COMMENT=0x08
    ADMINISTER=0x80

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )

class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    default=db.Column(db.Boolean,default=False,index=True)
    permissions=db.Column(db.Integer)
    user=db.relationship('User',backref='role',lazy='dynamic') #一个role对应多个user

    @staticmethod
    #使用几种权限组合成一个role
    def insert_roles():
        roles={
            'User':(Permission.FOLLOW |
                    Permission.COMMENT|
                    Permission.WRITE_ARTICLES,True),
            'Moderate':(Permission.FOLLOW |
                    Permission.COMMENT|
                    Permission.WRITE_ARTICLES|
                    Permission.MODERATE_COMMENT,False),
            'Administrator':(0xff,False)
        }
        #自动把所有Role（3个）添加进数据库
        for r in roles:
            role=Role.query.filter_by(name=r).first()
            if role is None: #没有就创建一个ROLE
                role=Role(name=r)
            role.permissions=roles[r][0]
            role.default=roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin,db.Model):
    __tablename__= 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me=db.Column(db.Text())
    last_seen=db.Column(db.DateTime(),default=datetime.utcnow)
    #一对多的关系：dynamic (不加载记录,但提供加载记录的查询)
    posts=db.relationship('Post',backref='author',lazy='dynamic')
    comments=db.relationship('Comment',backref='author',lazy='dynamic')
  #粉丝
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

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
        url='https://www.gravatar.com/avatar'
        hash=md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url,hash=hash,size=size,default=default,rating=rating)

    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)

    #是否是user的粉丝
    def is_following(self,user):
        return self.followed.filter(followers.c.followed_id==user.id).count()>0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    #生成令牌
    def get_reset_password_token(self,expires_in=600):
        return jwt.encode({'reset_password':self.id,'exp':time()+expires_in},
                          current_app.config['SECRET_KEY'],algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id=jwt.decode(token,current_app.config['SECRET_KEY'],algorithms=['HS256'])['reset_password']
        except:
            return None
        return User.query.get(id)

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            li=[]
            li.append(self.email)
            if li==current_app.config['ADMINS']: #好大一个坑，必需要用列表来判断
                self.role=Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role=Role.query.filter_by(default=True).first()
        db.session.commit()

    def __repr__(self):
        return '<User {}>'.format(self.username)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

LoginManager.anonymous_user=AnonymousUser

class Post(db.Model):
    __tablename__='post'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.String(140))
    body_html=db.Column(db.Text)
    timestamp=db.Column(db.DateTime, index=True, default=datetime.utcnow)
    #多的一方通过外键关联到user表
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    language=db.Column(db.String(5))
    comments=db.relationship('Comment',backref='post',lazy='dynamic')


    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p','tr','td','table','caption','head','meta',
                        'style','title']
        target.body_html=bleach.linkify(bleach.clean(
            markdown(value,output_format='html'),
            tags=allowed_tags,strip=True))

    def __repr__(self):
        return '<Post {}'.format(self.body)

db.event.listen(Post.body,'set',Post.on_changed_body)

class  Comment(db.Model):
    __tablename__='comments'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    body_html=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow())
    disabled=db.Column(db.Boolean)
    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    post_id=db.Column(db.Integer,db.ForeignKey('post.id'))
    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code',
                        'em', 'i',  'pre', 'strong']
        target.body_html=bleach.linkify(bleach.clean(
            markdown(value,output_format='html'),
            tags=allowed_tags,strip=True))

db.event.listen(Comment.body,'set',Comment.on_changed_body)

#用户加载函数
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
