#encoding:utf-8
import os
from flask import Flask,request
from config import Config

from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy#从包中导入类
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from logging.handlers import RotatingFileHandler, SMTPHandler
import logging
from flask_babel import Babel,lazy_gettext as _l

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)#数据库对象
migrate = Migrate(app,db)#迁移引擎对象

moment = Moment(app)#将日期和时间转换成目前可以想象到的所有格式



login = LoginManager(app)#用于管理用户登录状态，以便做到诸如用户可登录到应用程序
login.login_view = 'login'#login'值是登录视图函数（endpoint）名，换句话说该名称可用于url_for()函数的参数并返回对应的URL。'
login.login_message = _l('Please log in to access this page.')

mail = Mail(app)
bootstrap = Bootstrap(app)

babel = Babel(app)#用于翻译
#localeselector装饰器。对每个请求调用装饰函数，以选择一个用于该请求的语言翻译：
@babel.localeselector
def get_locale():
    #return request.accept_languages.best_match(app.config['LANGUAGES'])
    return 'zh_cn'

from app import routes,models,errors

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')



