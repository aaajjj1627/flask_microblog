#encoding:utf-8
from app import db,login
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin




class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
@login.user_loader

def load_user(id):
    return User.query.get(int(id))



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}'.format(self.body)


'''
db.relationship的第一个参数 表示关系“多”的模型类。如果模型稍后在模块中定义，则此参数可作为带有类名的字符串提供。
                 第二个参数backref定义将添加到“多”类的对象的字段的名称，该类指向“一”对象。这将添加一个post.author表达式，它将返回给定帖子的用户。
                 第三个参数lazy定义了如何发布对关系的数据库查询，这将在稍后讨论。
'''
'''
因为Flask-Login对数据库一无所知，所以在加载用户时需要应用程序的帮助。
因此，扩展期望应用程序配置一个用户加载函数，它可以被调用去加载给定ID的用户。
使用@login.user_loader装饰器向Flask-Login注册用户加载函数。Flask-Login传递给函数的id作为一个参数将是一个字符串，
所以需要将字符串类型转换为int型以供数据库使用数字ID
'''