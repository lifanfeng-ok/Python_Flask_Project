from flask import Flask
# from flask_bootstrap import Bootstrap
from datetime import datetime
from app import db


# from flask_bootstrap import Bootstrap
# from flask_redis import FlaskRedis
# from flask_sqlalchemy import SQLAlchemy
# from flask import Flask
# import pymysql
#
# app=Flask(__name__)
# app.config['SECRET_KEY']="123"
# app.config["SQLALCHEMY_DATABASE_URI"]='mysql+pymysql://root:lffhdhd123456@localhost:3306/community'
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=True
# app.debug=True
# bootstrap = Bootstrap(app)
# db=SQLAlchemy(app)

class Interface:
    _fields = []
    _rela_fields = []

    def to_dict(self):
        result = {key: self.__getattribute__(key) for key in self._fields}
        return result


class UserInfo(db.Model, Interface):
    __tablename__ = 'user_info'
    _fields = ['user_id', 'username', 'password', 'phone', 'info', 'face',
               'comment_num', 'collect_num', 'favorite_type', 'love_num', 'sex', 'fan', 'clock_num']
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    phone = db.Column(db.String(13))
    info = db.Column(db.Text)
    face = db.Column(db.String(100))
    comment_num = db.Column(db.Integer, default=0)
    collect_num = db.Column(db.Integer, default=0)
    favorite_type = db.Column(db.String(50))
    love_num = db.Column(db.Integer, default=0)
    sex = db.Column(db.String(10))
    fan = db.Column(db.Integer, default=0)
    clock_num = db.Column(db.Integer, default=0)
    Comment = db.relationship("Comment", backref='user_info')
    Collect = db.relationship("Collect", backref='user_info')
    Clock = db.relationship("Clock", backref='user_info')

    # log=db.relationship("Userlog",backref='user_info')
    def __repr__(self):
        return "<UserInfo %r>" % self.username


class video(db.Model, Interface):
    __tablename__ = 'video_info'
    _fields = ['id', 'name', 'url', 'iurl', 'watchnum', 'collectnum', 'real_collectnum',
               'videotype', 'addtime', 'info']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    url = db.Column(db.String(100), unique=True)
    iurl = db.Column(db.String(45))
    watchnum = db.Column(db.Integer, default=0)
    collectnum = db.Column(db.Integer, default=0)
    real_collectnum = db.Column(db.Integer, default=0)
    videotype = db.Column(db.String(20))
    info = db.Column(db.String(100))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    Comment = db.relationship("Comment", backref='video_info')
    Collect = db.relationship("Collect", backref='video_info')

    def __repr__(self):
        return "<UserInfo %r>" % self.name


class Collect(db.Model, Interface):
    __tablename__ = 'videocollect'
    _fields = ['id', 'video_id', 'user_id', 'addtime']
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video_info.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.user_id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)


class Comment(db.Model, Interface):
    __tablename__ = 'videocomment'
    _fields = ['id', 'content', 'video_id', 'user_id', 'addtime']
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    video_id = db.Column(db.Integer, db.ForeignKey('video_info.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.user_id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)


class User_relation(db.Model, Interface):
    __tablename__ = 'user_relation'
    _fields = ['id', 'love_id', 'be_id', 'addtime']
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    love_id = db.Column(db.Integer, db.ForeignKey('user_info.user_id'))
    be_id = db.Column(db.Integer, db.ForeignKey('user_info.user_id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    lover = db.relationship('UserInfo', foreign_keys=[love_id])
    be_lover = db.relationship('UserInfo', foreign_keys=[be_id])


class Clock(db.Model):
    __tablename__ = 'clock'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.user_id'))
    clock_type = db.Column(db.String(10))
    clock_time = db.Column(db.String(50))
    content = db.Column(db.String(60))
    good_count = db.Column(db.Integer, default=0)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)


class User(object):
    def __init__(self, username, user_id, face, info, comment_num, collect_num, love_num, common_num):
        self.username = username
        self.user_id = user_id
        self.face = face
        self.info = info
        self.comment_num = comment_num
        self.collect_num = collect_num
        self.love_num = love_num
        self.common_num = common_num


class Recommend_video(object):
    def __init__(self, id, name, iurl, watch_num, collect_num, comment_num, video_type, info):
        self.id = id
        self.name = name
        self.iurl = iurl
        self.watch_num = watch_num
        self.collect_num = collect_num
        self.comment_num = comment_num
        self.video_type = video_type
        self.info = info


class User_col(object):
    def __init__(self, title, type, iurl, collect_num, comment_num, col_addtime):
        self.title = title
        self.type = type
        self.iurl = iurl
        self.collect_num = collect_num
        self.comment_num = comment_num
        self.col_addtime = col_addtime


class User_collect(object):
    def __init__(self, username, user_id, face, info, comment_num, collect_num, love_num, collect_common_num):
        self.username = username
        self.user_id = user_id
        self.face = face
        self.info = info
        self.comment_num = comment_num
        self.collect_num = collect_num
        self.love_num = love_num
        self.collect_common_num = collect_common_num


class Admini(db.Model):
    __tablename__ = 'admini'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Admini %r>" % self.id

#
# class Userlog(db.Model):
#     __tablename__='userlog'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id=db.Column(db.Integer,db.ForeignKey("user_info.user_id"))
#     addtime = db.Column(db.DateTime, index=True, default=datetime.now)


# if __name__ == "__main__":
#     db.create_all()
