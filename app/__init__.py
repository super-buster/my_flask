from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_script import Manager
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
bootstrap=Bootstrap(app)
db=SQLAlchemy(app)
migrate=Migrate(app,db)
manage=Manager(app)
login=LoginManager(app)
login.login_view='login'

from app import routes,models