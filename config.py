import os
basedir=os.path.abspath(os.path.dirname(__file__)) #获得当前文件（比如配置文件）所在的路径

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MAIL_SERVER=os.environ.get('MAIL_SERVER')
    MAIL_PORT=int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS=['424295833@qq.com']
    POSTS_PER_PAGE=25
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES=['en','es','zh_CN']
    MS_TRANSLATOR_KEY=os.environ.get('MS_TRANSLATOR_KEY')
    LOG_TO_STDOUT=os.environ.get('LOG_TO_STDOUT')