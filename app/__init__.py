#encoding:utf-8
from flask import Flask
from config import Config

from flask_sqlalchemy import SQLAlchemy#从包中导入类
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)#数据库对象
migrate = Migrate(app,db)#迁移引擎对象

login = LoginManager(app)#用于管理用户登录状态，以便做到诸如用户可登录到应用程序
login.login_view = 'login'#login'值是登录视图函数（endpoint）名，换句话说该名称可用于url_for()函数的参数并返回对应的URL。'

from app import routes,models,errors

