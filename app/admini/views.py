# coding:utf8
import datetime
import uuid
from functools import wraps
import os
from flask import session, flash, redirect, url_for, request, render_template, g
from sqlalchemy import and_
from app import db, app
from . import admini
from app.admini.forms import LoginForm, Videoform, Editform
from app.model import Admini, video, Comment, Collect, UserInfo,Clock
from .. import db
from werkzeug.utils import secure_filename


def admin_login_req(f):
    """
    登录装饰器
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@admini.context_processor
def tpl_extra():
    """
    上下应用处理器
    """
    try:
        admin = Admini.query.filter_by(name=session["admin"]).first()
    except:
        admin = None
    data = dict(
        online_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        logo="avatar.png",
        admin=admin,
    )
    # 之后直接传个admin。取admin face字段即可
    return data


def change_filename(filename):
    """
    修改文件名称
    """
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + fileinfo[-1]
    return filename


@admini.route("/")
def index():
    g.logo = "avatar.png"
    return render_template("admini/index.html")


@admini.route("/login/", methods=["GET", "POST"])
def login():
    """
    后台登录
    """
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        uname = data["account"]
        pword = data["pwd"]
        if len(Admini.query.filter(and_(Admini.name == uname, Admini.password == pword)).all()) > 0:
            session["admin"] = uname
            session["admin_id"] = pword
            return redirect(request.args.get("next") or url_for("admini.index"))
        else:
            flash("密码错误", "err")
            return redirect(url_for('admini.login'))
    return render_template("admini/login.html", form=form)


@admin_login_req
@admini.route("/logout/")
def logout():
    session.pop("admin", None)
    session.pop("admin_id", None)
    # g.logo = ""
    return redirect(url_for("admini.login"))


@admin_login_req
@admini.route("/pwd/")
def pwd():
    return "<h1 style='color:red'>this is my</h1>"


@admin_login_req
@admini.route("/clock/")
def clock():
    userlist = UserInfo.query.order_by(UserInfo.clock_num.desc())
    user = []
    sit_up=0
    squat=0
    other=0
    for item in userlist:
        useritem ={
            "id": item.user_id,
            "username": item.username,
            "clock_num": item.clock_num
        }
        user.append(useritem)
    if len(user) > 8:
        user = user[0:8:1]
    clock = Clock.query
    for item in clock:
        if item.clock_type == '仰卧起坐':
            sit_up = sit_up + 1
        elif item.clock_type == '深蹲':
            squat = squat + 1
        else:
            other = other +1
    return render_template("admini/clock.html",user=user, sit_up = sit_up, squat = squat, other = other)


@admin_login_req
@admini.route("/video_add/", methods=["GET", "POST"])
def video_add():
    form = Videoform()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            # 创建一个多级目录
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"])
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        # 保存
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["DOWN_DIR"] + logo)
        # url,logo为上传视频,图片之后获取到的地址
        video22 = video(
            name=data["title"],
            url=url,
            iurl=logo,
            info=data["info"],
            videotype=data["type"],
            watchnum=0,
            collectnum=0,
            real_collectnum=0
        )
        db.session.add(video22)
        db.session.commit()
        flash("添加视频成功！", "ok")
        return redirect(url_for('admini.video_add'))
    return render_template("admini/video_add.html", form=form)


@admin_login_req
@admini.route("/video_list/<int:page>/")
def video_list(page=None):
    if page is None:
        page = 1
    page_data = video.query.paginate(page=page, per_page=6)
    return render_template("admini/video_list.html", page_data=page_data)


@admin_login_req
@admini.route("/user_list/<int:page>/")
def user_list(page=None):
    if page is None:
        page = 1
    page_data = UserInfo.query.order_by(
        UserInfo.addtime.desc()
    ).paginate(page=page, per_page=5)
    return render_template("admini/user_list.html", page_data=page_data)


@admini.route("/user_view/<int:id>/", methods=["GET"])
@admin_login_req
def user_view(id=None):
    """
    查看会员详情
    """
    from_page = request.args.get('fp')
    if not from_page:
        from_page = 1
    user = UserInfo.query.filter(UserInfo.user_id == id).first()
    return render_template("admini/user_view.html", user=user, from_page=from_page)


@admin_login_req
@admini.route("/comment_list/<int:page>/")
def comment_list(page=None):
    if page is None:
        page = 1
        # 通过评论join查询其相关的movie，和相关的用户。
        # 然后过滤出其中电影id等于评论电影id的电影，和用户id等于评论用户id的用户
    page_data = Comment.query.join(
        video
    ).join(
       UserInfo
    ).filter(
        video.id == Comment.video_id,
        UserInfo.user_id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=6)
    return render_template("admini/comment_list.html", page_data=page_data)


@admini.route("/comment_del/<int:id>/", methods=["GET"])
@admin_login_req
# @admin_auth
def comment_del(id=None):
    """
    删除评论
    """
    # 因为删除当前页。假如是最后一页，这一页已经不见了。回不到。
    from_page = int(request.args.get('fp')) - 1
    # 此处考虑全删完了，没法前挪的情况，0被视为false
    if not from_page:
        from_page = 1
    comment = Comment.query.filter(Comment.id == id).first()
    video22 = video.query.filter(video.id == comment.video_id).first()
    video22.collectnum = video22.collectnum - 1
    db.session.add(video22)
    db.session.commit()
    user = UserInfo.query.filter(UserInfo.user_id == comment.user_id).first()
    user.comment_num = user.comment_num - 1
    db.session.add(user)
    db.session.commit()
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功！", "ok")
    return redirect(url_for('admini.comment_list', page=from_page))


@admin_login_req
@admini.route("/video_col_list/<int:page>/")
def video_col_list(page=None):
    if page is None:
        page = 1
    page_data = Collect.query.join(
        video
    ).join(
        UserInfo
    ).filter(
        video.id == Collect.video_id,
        UserInfo.user_id == Collect.user_id
    ).order_by(
        Collect.addtime.desc()
    ).paginate(page=page, per_page=8)
    return render_template("admini/videocol_list.html", page_data=page_data)


@admini.route("/videocol_del/<int:id>/", methods=["GET"])
@admin_login_req
# @admin_auth
def videocol_del(id=None):
    """
    收藏删除
    """
    # 因为删除当前页。假如是最后一页，这一页已经不见了。回不到。
    from_page = int(request.args.get('fp')) - 1
    # 此处考虑全删完了，没法前挪的情况，0被视为false
    if not from_page:
        from_page = 1
    videocol = Collect.query.filter(Collect.id == id).first()
    video22 = video.query.filter(video.id == videocol.video_id).first()
    video22.real_collectnum = video22.real_collectnum - 1
    db.session.add(video22)
    db.session.commit()
    user = UserInfo.query.filter(UserInfo.user_id == videocol.user_id).first()
    user.collect_num = user.collect_num - 1
    db.session.add(user)
    db.session.commit()
    db.session.delete(videocol)
    db.session.commit()
    flash("删除收藏成功！", "ok")
    return redirect(url_for('admini.video_col_list', page=from_page))


@admin_login_req
@admini.route("/video_edit/<int:id>/", methods=["GET", "POST"])
def video_edit(id=None):
    form = Editform()
    # 因为是编辑，所以非空验证空
    form.url.validators = []
    form.logo.validators = []
    video22 = video.query.filter(video.id == id).first()
    if request.method == "GET":
        form.title.data = video22.name
        form.info.data = video22.info
        form.type.data = video22.videotype
    if form.validate_on_submit():
        data = form.data
        video_count = video.query.filter(video.name == data["title"]).count()
        # 存在一步名字叫这个的电影，有可能是它自己，也有可能是同名。如果是现在的movie不等于要提交的数据中title。那么说明有两个。
        if video_count == 1 and video22.name != data["title"]:
            flash("片名已经存在！", "err")
            return redirect(url_for('admini.video_edit', id=id))
        # 创建目录
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"])
        # 上传视频
        if form.url.data != "":
            file_url = secure_filename(form.url.data.filename)
            video22.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + video22.url)
        # 上传图片
        if form.logo.data != "":
            file_logo = secure_filename(form.logo.data.filename)
            video22.iurl = change_filename(file_logo)
            form.logo.data.save(app.config["DOWN_DIR"] + video22.iurl)
        video22.videotype = data["type"]
        video22.info = data["info"]
        video22.name = data["title"]
        db.session.add(video22)
        db.session.commit()
        flash("修改视频成功！", "ok")
        return redirect(url_for('admini.video_edit', id=id))
    return render_template("admini/video_edit.html", form=form, video=video22)


@admin_login_req
@admini.route("/video_del/<int:id>/")
def video_del(id=None):
    this_video = video.query.filter(video.id == id).first()
    collect = Collect.query.filter(Collect.video_id == id)
    for item in collect:
        user = UserInfo.query.filter(UserInfo.user_id == item.user_id).first()
        user.collect_num = user.collect_num - 1
        db.session.add(user)
        db.session.commit()
        db.session.delete(item)
        db.session.commit()
    comment = Comment.query.filter(Comment.video_id == id)
    for item in comment:
        user2 = UserInfo.query.filter(UserInfo.user_id == item.user_id).first()
        user2.comment_num = user2.comment_num - 1
        db.session.add(user2)
        db.session.commit()
        db.session.delete(item)
        db.session.commit()
    db.session.delete(this_video)
    db.session.commit()
    flash("电影删除成功", "ok")
    return redirect(url_for('admini.video_list', page=1))
