# coding:utf8
import os
#
from flask_bootstrap import Bootstrap
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import pymysql
app=Flask(__name__)
app.config['SECRET_KEY']="123"
app.config["SQLALCHEMY_DATABASE_URI"]='mysql+pymysql://root:lffhdhd123456@localhost:3306/community'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=True
app.debug=True
bootstrap = Bootstrap(app)
db=SQLAlchemy(app)
app.config['REDIS_URL'] = "redis://localhost:6379/1"
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
app.config["FC_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")
rd = FlaskRedis(app)
from app.home import home as home_blueprint
from app.admini import admini as admini_blueprint
app.register_blueprint(home_blueprint)
app.register_blueprint(admini_blueprint,url_prefix="/admini")
