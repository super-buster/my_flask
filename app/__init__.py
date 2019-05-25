# -*- coding: utf-8 -*-
from flask import Flask,current_app,request
from config import Config
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_script import Manager
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from flask_pagedown import PageDown
from elasticsearch import Elasticsearch
import logging
from logging.handlers import SMTPHandler ,RotatingFileHandler
import os
from flask_ckeditor import CKEditor
from flask_admin import Admin
from app.admins.models import UserModelView, PostModelView, CommentModelView,MyAdminIndexView
bootstrap=Bootstrap()
db=SQLAlchemy()
migrate=Migrate()
manage=Manager()
login=LoginManager()
login.login_view='auth.login'
login.login_message = _l('Please log in to access this page.')
mail=Mail()
moment=Moment()
babel=Babel()
pagedown=PageDown()
ckeditor=CKEditor()
admin = Admin(name=_l('Dashboard'),template_mode='bootstrap3',index_view=MyAdminIndexView())


def creat_app(config_clas=Config):
    app = Flask(__name__,static_url_path='/static')

    app.config.from_object(config_clas)
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None
    db.init_app(app)
    migrate.init_app(app,db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    pagedown.init_app(app)
    ckeditor.init_app(app)
    admin.init_app(app)

    from .models import User,Permission,Post,Comment

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.admins import bp as admins_bp
    app.register_blueprint(admins_bp)

    admin.add_view(UserModelView(User, db.session, category=_l('People')))
    admin.add_view(PostModelView(Post, db.session, category=_l('Things')))
    admin.add_view(CommentModelView(Comment, db.session, category=_l('Things')))

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_USERNAME'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config['LOG_TO_STDOUT']:
            stream_handler=logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                               backupCount=10)
            #设置时间，日志级别，用户输出的信息，调用日志输出函数的模块的文件名，所在的代码行
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info('Microblog startup')

    @app.after_request
    def add_header(response):
        # response.cache_control.no_store = True
        if 'Cache-Control' not in response.headers:
            response.headers['Cache-Control'] = 'no-store'
        return response

    return app

@babel.localeselector
def get_locale():
     return request.accept_languages.best_match(current_app.config['LANGUAGES'])
    #return 'zh'
from app import models