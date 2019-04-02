#encoding:utf-8
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
basedir = os.path.abspath(os.path.dirname(__file__))#获取当前.py文件的绝对路径

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you will never guess'

	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
							  'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
	MAIL_SERVER = os.environ.get('MAIL_SERVER')
	MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
	MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	ADMINS = ['another-qq@qq.com']

	LANGUAGES = ['en', 'zh']

	POSTS_PER_PAGE = 10


