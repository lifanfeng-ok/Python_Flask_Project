# coding:utf8
from . import admini

@admini.route("/")
def index():
    return "<h1 style='color:red'>this is home</h1>"