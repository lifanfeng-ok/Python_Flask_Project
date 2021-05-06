# coding:utf8
import datetime
import math
import os
import uuid
from werkzeug.utils import secure_filename
from app.model import UserInfo, video, Comment, Collect, User_relation, User, User_collect, Clock, Recommend_video
from . import home
from flask import render_template, redirect, url_for, session, flash, request, Response, jsonify
from app.home.forms import LoginForm, RegisterForm, EditForm, CommentForm, Submit
from functools import wraps
from sqlalchemy import and_
from app import db, rd, app
import datetime
import json


def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def change_filename(filename):
    """
    修改文件名称
    """
    fileinfo = os.path.splitext(filename)
    filename = "a" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + \
               str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


@home.route("/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        uname = form.username.data
        pword = form.password.data

        if len(UserInfo.query.filter(and_(UserInfo.username == uname, UserInfo.password == pword)).all()) > 0:
            session["user"] = uname

            return redirect(request.args.get("next") or url_for("home.index", page=1))
        else:
            flash("用户名或密码错误")
            return redirect(url_for('home.login'))
    return render_template("home/login.html", form=form)


@home.route("/android_login/", methods=['GET', 'POST'])
def android_login():
    stuname = request.args.get('name')
    password = request.args.get('password')
    if len(UserInfo.query.filter(and_(UserInfo.username == stuname, UserInfo.password == password)).all()) > 0:
        result = dict(ok=1)
    else:
        result = dict(ok=0)
    # return jsonify(result)
    import json
    return json.dumps(result)


@home.route("/android_register/", methods=['GET', 'POST'])
def android_register():
    name = request.args.get('name')
    password = request.args.get('password')
    phone = request.args.get('phone')
    sex = request.args.get('sex')
    if len(UserInfo.query.filter(UserInfo.username == name).all()) > 0:
        result = {
            "ok": 0,
            "data": "failed"
        }
    else:
        new_user = UserInfo(
            username=name,
            password=password,
            sex=sex,
            phone=phone
        )
        db.session.add(new_user)
        db.session.commit()
        result = {
            "ok": 1,
            "data": "successed"
        }
    import json
    return json.dumps(result)


@home.route("/android_getvideo/", methods=['GET', 'POST'])
def android_getvideo():
    videodata = video.query
    import json
    response = json.dumps([item.to_dict() for item in videodata])
    return response


@home.route("/android_getuser/", methods=['GET', 'POST'])
def android_getuser():
    name = request.args.get('name')
    user = UserInfo.query.filter(UserInfo.username == name)
    response = json.dumps([item.to_dict() for item in user])
    return response


@home.route("/android_getcol/", methods=['GET', 'POST'])
def android_getcol():
    name = request.args.get('name')
    user = UserInfo.query.filter(UserInfo.username == name).first()
    col_list = []
    col = Collect.query.filter(Collect.user_id == user.user_id)
    for item in col:
        video_item = video.query.filter(video.id == item.video_id).first()
        col_item = {
            "title": video_item.name,
            "type": video_item.videotype,
            "iurl": video_item.iurl,
            "collect_num": video_item.real_collectnum,
            "comment_num": video_item.collectnum,
            "col_addtime": item.addtime
        }
        col_list.append(col_item)
    response = json.dumps(col_list, cls=DateEncoder)
    return response


@home.route("/android_getnotice/", methods=['GET', 'POST'])
def android_getnotice():
    name = request.args.get('name')
    user = UserInfo.query.filter(UserInfo.username == name).first()
    notice = UserInfo.query.join(User_relation, UserInfo.user_id == User_relation.be_id).filter(
        User_relation.love_id == user.user_id,
    )
    response = json.dumps([item.to_dict() for item in notice])
    return response


@home.route("/android_getcomment/", methods=['GET', 'POST'])
def android_getcomment():
    video_id = request.args.get('id')
    com = Comment.query.filter(Comment.video_id == video_id)
    comment_list = []
    for item in com:
        user = UserInfo.query.filter(UserInfo.user_id == item.user_id).first()
        com_item = {
            "username": user.username,
            "iurl": user.face,
            "info": item.content
        }
        comment_list.append(com_item)
    response = json.dumps(comment_list)
    return response


@home.route("/android_iscol/", methods=['GET', 'POST'])
def android_iscol():
    mid = request.args.get('vid')
    username = request.args.get('username')
    user = UserInfo.query.filter(UserInfo.username == username).first()
    moviecol = Collect.query.filter_by(
        video_id=int(mid),
        user_id=int(user.user_id)
    ).count()
    if moviecol == 1:
        # 已收藏
        data = dict(ok=0)
    else:
        data = dict(ok=1)
    return json.dumps(data)


@home.route("/android_addcol/", methods=['GET', 'POST'])
def android_addcol():
    mid = request.args.get('vid')
    username = request.args.get('username')
    user = UserInfo.query.filter(UserInfo.username == username).first()
    moviecol = Collect.query.filter_by(
        video_id=int(mid),
        user_id=int(user.user_id)
    ).count()
    video2 = video.query.filter(video.id == int(mid)).first()
    if moviecol == 1:
        # 已收藏
        data = dict(ok=0)
    if moviecol == 0:
        # 未收藏
        moviecol = Collect(
            video_id=int(mid),
            user_id=int(user.user_id)
        )
        db.session.add(moviecol)
        db.session.commit()
        user.collect_num = user.collect_num + 1
        db.session.add(user)
        db.session.commit()
        video2.real_collectnum += 1
        db.session.add(video2)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)


@home.route("/android_addcom/", methods=['GET', 'POST'])
def android_addcom():
    vid = request.args.get('vid')
    username = request.args.get('username')
    content = request.args.get('content')
    user = UserInfo.query.filter(UserInfo.username == username).first()
    video1 = video.query.filter(
        video.id == int(vid)
    ).first()
    newcomment = Comment(
        content=content,
        video_id=vid,
        user_id=user.user_id
    )
    db.session.add(newcomment)
    db.session.commit()
    video1.collectnum = video1.collectnum + 1
    db.session.add(video1)
    db.session.commit()
    user.comment_num = user.comment_num + 1
    db.session.add(user)
    db.session.commit()
    data = {
        "ok": 1,
        "iurl": user.face
    }
    return json.dumps(data)


@home.route("/android_getrecommend1/", methods=['GET', 'POST'])
def android_getrecommend1():
    username = request.args.get('username')
    user = UserInfo.query.filter(UserInfo.username == username).first()
    love_id = []
    wholeuser = []
    wholeuser2 = []
    user_common = {}
    Usermodel = []
    whole_user = UserInfo.query.filter(UserInfo.username != username)
    data2 = UserInfo.query.join(User_relation, UserInfo.user_id == User_relation.be_id).filter(
        User_relation.love_id == user.user_id,
    )
    for k in whole_user:
        wholeuser.append(k.user_id)
        wholeuser2.append(k.user_id)
        user_common[k.user_id] = 0
    for i in data2:
        love_id.append(i.user_id)
    for k in wholeuser:
        for j in love_id:
            if k == j:
                wholeuser2.remove(k)
                user_common.pop(k)
    for m in wholeuser2:
        for z in love_id:
            if User_relation.query.filter(User_relation.love_id == m,
                                          User_relation.be_id == z).count() == 1:
                user_common[m] += 1
    for x in user_common:
        if user_common[x] > 0:
            column = UserInfo.query.filter(UserInfo.user_id == x)
            user11 = User(
                column[0].username,
                column[0].user_id,
                column[0].face,
                column[0].info,
                column[0].comment_num,
                column[0].collect_num,
                column[0].love_num,
                user_common[x]
            )
            Usermodel.append(user11)
    if len(Usermodel) > 3:
        Usermodel = Usermodel[0:3:1]
    recommend_list = []
    for i in Usermodel:
        item = {
            "name": i.username,
            "iurl": i.face,
            "collect": i.collect_num,
            "comment": i.comment_num,
            "notice": i.love_num,
            "common": i.common_num
        }
        recommend_list.append(item)
    response = json.dumps(recommend_list)
    return response


@home.route("/android_getrecommend2/", methods=['GET', 'POST'])
def android_getrecommend2():
    username = request.args.get('username')
    user = UserInfo.query.filter(UserInfo.username == username).first()
    love_id = []
    wholeuser = []
    wholeuser2 = []
    user_common = {}
    video_common = {}
    video_common2 = {}
    final = {}
    Usermodel = []
    Usermodel2 = []
    whole_user = UserInfo.query.filter(UserInfo.username != username)
    data2 = UserInfo.query.join(User_relation, UserInfo.user_id == User_relation.be_id).filter(
        User_relation.love_id == user.user_id,
    )
    data3 = Collect.query.filter(Collect.user_id == user.user_id)
    collect_num = Collect.query.filter(Collect.user_id == user.user_id).count()
    for k in whole_user:
        wholeuser.append(k.user_id)
        wholeuser2.append(k.user_id)
        user_common[k.user_id] = 0
    for i in data2:
        love_id.append(i.user_id)
    for k in wholeuser:
        for j in love_id:
            if k == j:
                wholeuser2.remove(k)
                user_common.pop(k)
    for m in wholeuser2:
        for z in love_id:
            if User_relation.query.filter(User_relation.love_id == m,
                                          User_relation.be_id == z).count() == 1:
                user_common[m] += 1
    for x in user_common:
        if user_common[x] > 0:
            column = UserInfo.query.filter(UserInfo.user_id == x)
            user11 = User(
                column[0].username,
                column[0].user_id,
                column[0].face,
                column[0].info,
                column[0].comment_num,
                column[0].collect_num,
                column[0].love_num,
                user_common[x]
            )
            Usermodel.append(user11)
    if len(Usermodel) > 3:
        Usermodel = Usermodel[0:3:1]
    for i in wholeuser2:
        video_common[i] = 0
        video_common2[i] = 0
        potential_lovenum = User_relation.query.filter(User_relation.love_id == i).count()
        if user_common[i] != 0:
            user_common[i] = user_common[i] / (math.sqrt(potential_lovenum * len(love_id)))
    for v in wholeuser2:
        potential_love_video = Collect.query.filter(Collect.user_id == v)
        for i in potential_love_video:
            for k in data3:
                if k.video_id == i.video_id:
                    video_common[v] += 1
                    video_common2[v] += 1
    for i in wholeuser2:
        potential_collectnum = Collect.query.filter(Collect.user_id == i).count()
        if video_common[i] != 0:
            video_common[i] = video_common[i] / (math.sqrt(potential_collectnum * collect_num))
    alpha = 0.5
    for i in user_common:
        for j in video_common:
            if i == j:
                final[i] = alpha * user_common[i] + (1 - alpha) * video_common[i]
    sortedData = dict(sorted(final.items(), key=lambda data: data[1], reverse=True))
    for i in sortedData:
        if sortedData[i] > 0:
            column = UserInfo.query.filter(UserInfo.user_id == i)
            user22 = User_collect(
                column[0].username,
                column[0].user_id,
                column[0].face,
                column[0].info,
                column[0].comment_num,
                column[0].collect_num,
                column[0].love_num,
                video_common2[i]
            )
            Usermodel2.append(user22)
    if len(Usermodel2) > 3:
        Usermodel2 = Usermodel2[0:3:1]
    recommend_list2 = []
    for i in Usermodel2:
        item = {
            "username": i.username,
            "iurl": i.face,
            "collect": i.collect_num,
            "comment": i.comment_num,
            "notice": i.love_num,
            "common2": i.collect_common_num
        }
        recommend_list2.append(item)
    response=json.dumps(recommend_list2)
    return response


@home.route("/android_addlove/", methods=['GET', 'POST'])
def android_addlove():
    username = request.args.get('username')
    his_name = request.args.get('his_name')
    user = UserInfo.query.filter(UserInfo.username == username).first()
    user2 = UserInfo.query.filter(UserInfo.username == his_name).first()
    usercol = User_relation.query.filter_by(
        be_id=int(user2.user_id),
        love_id=int(user.user_id)
    ).count()
    if usercol == 1:
        # 已收藏
        data = dict(ok=0)
    if usercol == 0:
        # 未收藏
        love = User_relation(
            be_id=int(user2.user_id),
            love_id=int(user.user_id)
        )
        db.session.add(love)
        db.session.commit()
        user.love_num = user.love_num + 1
        db.session.add(user)
        db.session.commit()
        user2.fan = user2.fan + 1
        db.session.add(user2)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)


@home.route("/android_addclock/", methods=['GET', 'POST'])
def android_addclock():
    username = request.args.get('name')
    type = request.args.get('type')
    time = request.args.get('time')
    content = request.args.get('content')
    user = UserInfo.query.filter(UserInfo.username == username).first()
    new_clock=Clock(
        user_id= user.user_id,
        clock_type=type,
        clock_time=time,
        content=content
    )
    db.session.add(new_clock)
    db.session.commit()
    user.clock_num =user.clock_num+1
    db.session.add(user)
    db.session.commit()
    data = dict(ok=1)
    return json.dumps(data)


@home.route("/android_isclock/", methods=['GET', 'POST'])
def android_isclock():
    username = request.args.get('name')
    user = UserInfo.query.filter(UserInfo.username == username).first()
    clock_record = Clock.query.filter( Clock.user_id == user.user_id)
    clock = []
    for item in clock_record:
        clock_item = {
            "date": item.addtime,
            "date_type": "1"
        }
        clock.append(clock_item)
    response = json.dumps(clock,cls=DateEnconding)
    return response


@home.route("/android_get_other_clock/", methods=['GET','POST'])
def android_get_other_clock():
    username = request.args.get('username')
    user = UserInfo.query.filter(UserInfo.username == username).first()
    data2 = Clock.query.join(User_relation, Clock.user_id == User_relation.be_id).filter(
        User_relation.love_id == user.user_id
    ).order_by(Clock.addtime.desc())
    clock_list=[]
    for item in data2:
        this_user = UserInfo.query.filter(UserInfo.user_id == item.user_id).first()
        clock_item={
            "id": item.id,
            "name": this_user.username,
            "iurl": this_user.face,
            "good_num": item.good_count,
            "type": item.clock_type,
            "time": item.clock_time,
            "content": item.content,
            "publish_time": item.addtime
        }
        clock_list.append(clock_item)
    if len(clock_list) > 4:
        clock_list = clock_list[0:5:1]
    response = json.dumps(clock_list,cls=DateEnconding)
    return response


@home.route("/android_good_other_clock/", methods=['GET','POST'])
def android_good_other_clock():
    clock_id=request.args.get('clock_id')
    clock= Clock.query.filter(Clock.id == clock_id).first()
    clock.good_count= clock.good_count+1
    db.session.add(clock)
    db.session.commit()
    data = dict(ok=1)
    return json.dumps(data)


@home.route("/android_max_other_clock/", methods=['GET','POST'])
def android_max_other_clock():
    username = request.args.get('username')
    user = UserInfo.query.filter(UserInfo.username == username).first()
    data2 = UserInfo.query.join(User_relation, UserInfo.user_id == User_relation.be_id).filter(
        User_relation.love_id == user.user_id
    ).order_by(UserInfo.clock_num.desc())
    max_record=[]
    i=1
    for item in data2:
        max_item={
            "order":i,
            "username": item.username,
            "iurl": item.face,
            "clock_num": item.clock_num
        }
        max_record.append(max_item)
        i=i+1
    if len(max_record) > 2:
        max_record = max_record[0:3:1]
    response = json.dumps(max_record)
    return response

class DateEnconding(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')


@home.route("/android_edit/", methods=['GET', 'POST'])
def android_edit():
    username = request.args.get('username')
    password = request.args.get('password')
    phone = request.args.get('phone')
    info = request.args.get('info')
    user = UserInfo.query.filter(UserInfo.username == username).first()
    user.password = password
    user.phone = phone
    user.info = info
    db.session.add(user)
    db.session.commit()
    data = dict(ok=1)
    return json.dumps(data)



@home.route("/logout", methods=['GET'])
@user_login_req
def logout():
    session.pop("user", None)
    return redirect(url_for("home.login"))


@home.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        stuname = request.form.get('stuname')
        sex = request.form.get('sex')
        password = request.form.get('password')
        phone = request.form.get('phone')
        if len(UserInfo.query.filter(UserInfo.username == stuname).all()) > 0:
            flash("该账号已被注册")
        else:
            new_user = UserInfo(
                username=stuname,
                password=password,
                sex=sex,
                phone=phone
            )
            db.session.add(new_user)
            db.session.commit()
            flash("注册成功!")
            return redirect(url_for('home.login'))
    return render_template("home/register.html")


@home.route("/index/<int:page>/", methods=['GET', 'POST'])
@user_login_req
def index(page=None):
    data = video.query
    videotype = request.args.get("videotype", 0)
    if int(videotype) != 0:
        if int(videotype) == 1:
            data = data.filter_by(videotype="深蹲")
        elif int(videotype) == 2:
            data = data.filter_by(videotype="仰卧起坐")
        elif int(videotype) == 3:
            data = data.filter_by(videotype="俯卧撑")
        else:
            data = data.filter_by(videotype="器械运动")
    watchnum = request.args.get("watchnum", 0)
    if int(watchnum) != 0:
        if int(watchnum) == 1:
            data = data.order_by(
                video.watchnum.desc()
            )
        else:
            data = data.order_by(
                video.watchnum.asc()
            )
    collectnum = request.args.get("collectnum", 0)
    if int(collectnum) != 0:
        if int(collectnum) == 1:
            data = data.order_by(
                video.collectnum.desc()
            )
        else:
            data = data.order_by(
                video.collectnum.asc()
            )
    if page is None:
        page = 1
    data = data.paginate(page=page, per_page=4)
    p = dict(
        videotype=videotype,
        watchnum=watchnum,
        collectnum=collectnum,
    )

    return render_template("home/index.html", p=p, data=data)


@home.route("/animation", methods=['GET', 'POST'])
@user_login_req
def animation():
    return render_template("home/animation.html")


@home.route("/center", methods=['GET', 'POST'])
@user_login_req
def center():
    form = EditForm()
    user = UserInfo.query.filter(UserInfo.username == session["user"]).first()
    form.face.validators = []
    if request.method == "GET":
        form.username.data = user.username
        form.password.data = user.password
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        name_count = UserInfo.query.filter_by(username=data["username"]).count()
        if data["username"] != user.username and name_count == 1:
            flash("昵称已经存在!", "err")
            return redirect(url_for("home.center"))
        phone_count = UserInfo.query.filter_by(phone=data["phone"]).count()
        if data["phone"] != user.phone and phone_count == 1:
            flash("手机已经存在!", "err")
            return redirect(url_for("home.center"))
        if form.face.data != "":
            file_face = secure_filename(form.face.data.filename)
            if not os.path.exists(app.config["FC_DIR"]):
                os.makedirs(app.config["FC_DIR"])
                os.chmod(app.config["FC_DIR"])
            user.face = change_filename(file_face)
            form.face.data.save(app.config["FC_DIR"] + user.face)
        user.username = data["username"]
        user.password = data["password"]
        user.phone = data["phone"]
        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("修改成功,请重新登陆", "ok")
        return redirect(url_for("home.login"))
    return render_template("home/center.html", form=form, user=user)


@home.route("/edit", methods=['GET', 'POST'])
@user_login_req
def edit():
    return render_template("home/edit.html")


@home.route("/comments/<int:page>/", methods=['GET', 'POST'])
@user_login_req
def comments(page=None):
    user = UserInfo.query.filter(UserInfo.username == session["user"]).first()
    data = Comment.query.join(
        video
    ).join(
        UserInfo
    ).filter(video.id == Comment.video_id, UserInfo.user_id == user.user_id).order_by(Comment.addtime.desc())
    if page == None:
        page = 1
    data = data.paginate(page=page, per_page=4)
    return render_template("home/comments.html", data=data)


@home.route("/search/<int:page>/", methods=['GET', 'POST'])
@user_login_req
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get("key", "")
    video_count = video.query.filter(
        video.name.ilike('%' + key + '%')
    ).count()
    data = video.query.filter(
        video.name.ilike('%' + key + '%')
    ).paginate(page=page, per_page=10)
    data.key = key
    return render_template("home/search.html", video_count=video_count, key=key, data=data
                           )


@home.route("/play/<int:id>/<int:page>/", methods=['GET', 'POST'])
@user_login_req
def play(id=None, page=None):
    form = CommentForm()
    user = UserInfo.query.filter(UserInfo.username == session["user"]).first()
    video1 = video.query.filter(
        video.id == int(id)
    ).first()
    video1.watchnum = video1.watchnum + 1
    db.session.add(video1)
    db.session.commit()
    if page == None:
        page = 1
    data = Comment.query.join(video).join(UserInfo).filter(
        video.id == video1.id, UserInfo.user_id == Comment.user_id).order_by(
        Comment.addtime.desc()).paginate(page=page, per_page=5)
    if form.validate_on_submit():
        data1 = form.data
        newcomment = Comment(
            content=data1["content"],
            video_id=video1.id,
            user_id=user.user_id
        )
        db.session.add(newcomment)
        db.session.commit()
        video1.collectnum = video1.collectnum + 1
        video1.watchnum = video1.watchnum - 2
        db.session.add(video1)
        db.session.commit()
        user.comment_num = user.comment_num + 1
        db.session.add(user)
        db.session.commit()
        flash("评论成功")
        return redirect(url_for('home.play', id=video1.id, page=1))

    return render_template("home/play.html", video=video1, form=form, data=data)


@home.route('/moviecol/add/', methods=['GET'])
@user_login_req
def moviecol_add():
    mid = request.args.get('mid', '')
    user = UserInfo.query.filter(UserInfo.username == session["user"]).first()
    moviecol = Collect.query.filter_by(
        video_id=int(mid),
        user_id=int(user.user_id)
    ).count()
    video2 = video.query.filter(video.id == int(mid)).first()
    if moviecol == 1:
        # 已收藏
        data = dict(ok=0)
    if moviecol == 0:
        # 未收藏
        moviecol = Collect(
            video_id=int(mid),
            user_id=int(user.user_id)
        )
        db.session.add(moviecol)
        db.session.commit()
        user.collect_num = user.collect_num + 1
        db.session.add(user)
        db.session.commit()
        video2.real_collectnum += 1
        db.session.add(video2)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)


@home.route('/video_col/<int:page>/')
@user_login_req
def video_col(page=None):
    user = UserInfo.query.filter(UserInfo.username == session["user"]).first()
    if page == None:
        page = 1
    data = Collect.query.join(video).join(UserInfo).filter(
        video.id == Collect.video_id,
        Collect.user_id == int(user.user_id)
    ).order_by(Collect.addtime.desc()).paginate(page=page, per_page=5)
    return render_template("home/video_col.html", data=data)


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


@home.route('/video_col2/')
def video_col2():
    user = UserInfo.query.filter(UserInfo.username == session["user"]).first()
    data = Collect.query.join(video).join(UserInfo).filter(
        video.id == Collect.video_id,
        Collect.user_id == int(user.user_id)
    ).order_by(Collect.addtime.desc())
    import json
    response = json.dumps([item.to_dict() for item in data], cls=DateEncoder)
    return response


@home.route("/video22/<int:id>/<int:page>/", methods=['GET', 'POST'])
@user_login_req
def video22(id=None, page=None):
    form = CommentForm()
    user = UserInfo.query.filter(UserInfo.username == session["user"]).first()
    video1 = video.query.filter(
        video.id == int(id)
    ).first()
    video1.watchnum = video1.watchnum + 1
    db.session.add(video1)
    db.session.commit()
    if page == None:
        page = 1
    data = Comment.query.join(video).join(UserInfo).filter(
        video.id == video1.id, UserInfo.user_id == Comment.user_id).order_by(
        Comment.addtime.desc()).paginate(page=page, per_page=5)
    if form.validate_on_submit():
        data1 = form.data
        newcomment = Comment(
            content=data1["content"],
            video_id=video1.id,
            user_id=user.user_id
        )
        db.session.add(newcomment)
        db.session.commit()
        video1.collectnum = video1.collectnum + 1
        video1.watchnum = video1.watchnum - 2
        db.session.add(video1)
        db.session.commit()
        user.comment_num = user.comment_num + 1
        db.session.add(user)
        db.session.commit()
        flash("评论成功")
        return redirect(url_for('home.video22', id=video1.id, page=1))

    return render_template("home/video22.html", video=video1, form=form, data=data)


@home.route("/dm/", methods=["GET", "POST"])
def dm():
    import json
    if request.method == "GET":
        # 获取弹幕消息队列
        id = request.args.get('id')
        key = "video" + str(id)
        if rd.llen(key):
            msgs = rd.lrange(key, 0, 2999)
            res = {
                "code": 1,
                "danmaku": [json.loads(v) for v in msgs]
            }
        else:
            res = {
                "code": 1,
                "danmaku": []
            }
        resp = json.dumps(res)
    if request.method == "POST":
        # 添加弹幕
        id = request.args.get('id')
        data = json.loads(request.get_data())
        msg = {
            "__v": 0,
            "author": data["author"],
            "time": data["time"],
            "text": data["text"],
            "color": data["color"],
            "type": data['type'],
            "ip": request.remote_addr,
            "_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
            "player": [
                data["player"]
            ]
        }
        res = {
            "code": 1,
            "data": msg
        }
        resp = json.dumps(res)
        rd.lpush("video" + str(data["player"]), json.dumps(msg))
    return Response(resp, mimetype='application/json')


@home.route('/recommend_user/<int:page>', methods=["GET", "POST"])
@user_login_req
def recommend_user(page=None):
    import math
    if page == None:
        page = 1
    key = request.args.get("key", "")
    user = UserInfo.query.filter(UserInfo.username == session["user"]).first()
    love_id = []
    wholeuser = []
    wholeuser2 = []
    user_common = {}
    video_common = {}
    video_common2 = {}
    final = {}
    Usermodel = []
    Usermodel2 = []
    whole_user = UserInfo.query.filter(UserInfo.username != session["user"])
    data = UserInfo.query.filter(
        UserInfo.username.ilike('%' + key + '%'), UserInfo.username != session["user"]
    ).paginate(page=page, per_page=6)
    data.key = key
    data2 = UserInfo.query.join(User_relation, UserInfo.user_id == User_relation.be_id).filter(
        User_relation.love_id == user.user_id,
    )
    data3 = Collect.query.filter(Collect.user_id == user.user_id)
    collect_num = Collect.query.filter(Collect.user_id == user.user_id).count()
    for k in whole_user:
        wholeuser.append(k.user_id)
        wholeuser2.append(k.user_id)
        user_common[k.user_id] = 0
    for i in data2:
        love_id.append(i.user_id)
    for k in wholeuser:
        for j in love_id:
            if k == j:
                wholeuser2.remove(k)
                user_common.pop(k)
    for m in wholeuser2:
        for z in love_id:
            if User_relation.query.filter(User_relation.love_id == m,
                                          User_relation.be_id == z).count() == 1:
                user_common[m] += 1
    for x in user_common:
        if user_common[x] > 0:
            column = UserInfo.query.filter(UserInfo.user_id == x)
            user11 = User(
                column[0].username,
                column[0].user_id,
                column[0].face,
                column[0].info,
                column[0].comment_num,
                column[0].collect_num,
                column[0].love_num,
                user_common[x]
            )
            Usermodel.append(user11)
    if len(Usermodel) > 3:
        Usermodel = Usermodel[0:3:1]
    for i in wholeuser2:
        video_common[i] = 0
        video_common2[i] = 0
        potential_lovenum = User_relation.query.filter(User_relation.love_id == i).count()
        if user_common[i] != 0:
            user_common[i] = user_common[i] / (math.sqrt(potential_lovenum * len(love_id)))
    for v in wholeuser2:
        potential_love_video = Collect.query.filter(Collect.user_id == v)
        for i in potential_love_video:
            for k in data3:
                if k.video_id == i.video_id:
                    video_common[v] += 1
                    video_common2[v] += 1
    for i in wholeuser2:
        potential_collectnum = Collect.query.filter(Collect.user_id == i).count()
        if video_common[i] != 0:
            video_common[i] = video_common[i] / (math.sqrt(potential_collectnum * collect_num))
    print(user_common)
    print(video_common)
    alpha = 0.5
    for i in user_common:
        for j in video_common:
            if i == j:
                final[i] = alpha * user_common[i] + (1 - alpha) * video_common[i]
    print(final)
    sortedData = dict(sorted(final.items(), key=lambda data: data[1], reverse=True))
    print(sortedData)
    for i in sortedData:
        if sortedData[i] > 0:
            column = UserInfo.query.filter(UserInfo.user_id == i)
            user22 = User_collect(
                column[0].username,
                column[0].user_id,
                column[0].face,
                column[0].info,
                column[0].comment_num,
                column[0].collect_num,
                column[0].love_num,
                video_common2[i]
            )
            Usermodel2.append(user22)
    if len(Usermodel2) > 3:
        Usermodel2 = Usermodel2[0:3:1]
    return render_template("home/recommend_user.html", data=data, data2=Usermodel, data3=Usermodel2)


@home.route('/recommend_video/', methods=['GET'])
@user_login_req
def recommend_video():
    import math
    user = UserInfo.query.filter(UserInfo.username == session["user"]).first()
    love_id = []
    wholeuser = []
    wholeuser2 = []
    user_common = {}
    video_common = {}
    video_common2 = {}
    final = {}
    Usermodel = []
    Usermodel2 = []
    whole_user = UserInfo.query.filter(UserInfo.username != session["user"])
    data2 = UserInfo.query.join(User_relation, UserInfo.user_id == User_relation.be_id).filter(
        User_relation.love_id == user.user_id,
    )
    data3 = Collect.query.filter(Collect.user_id == user.user_id)
    collect_num = Collect.query.filter(Collect.user_id == user.user_id).count()
    for k in whole_user:
        wholeuser.append(k.user_id)
        wholeuser2.append(k.user_id)
        user_common[k.user_id] = 0
    for i in data2:
        love_id.append(i.user_id)
    for k in wholeuser:
        for j in love_id:
            if k == j:
                wholeuser2.remove(k)
                user_common.pop(k)
    for m in wholeuser2:
        for z in love_id:
            if User_relation.query.filter(User_relation.love_id == m,
                                          User_relation.be_id == z).count() == 1:
                user_common[m] += 1
    for x in user_common:
        if user_common[x] > 0:
            column = UserInfo.query.filter(UserInfo.user_id == x)
            user11 = User(
                column[0].username,
                column[0].user_id,
                column[0].face,
                column[0].info,
                column[0].comment_num,
                column[0].collect_num,
                column[0].love_num,
                user_common[x]
            )
            Usermodel.append(user11)
    if len(Usermodel) > 3:
        Usermodel = Usermodel[0:3:1]
    for i in wholeuser2:
        video_common[i] = 0
        video_common2[i] = 0
        potential_lovenum = User_relation.query.filter(User_relation.love_id == i).count()
        if user_common[i] != 0:
            user_common[i] = user_common[i] / (math.sqrt(potential_lovenum * len(love_id)))
    for v in wholeuser2:
        potential_love_video = Collect.query.filter(Collect.user_id == v)
        for i in potential_love_video:
            for k in data3:
                if k.video_id == i.video_id:
                    video_common[v] += 1
                    video_common2[v] += 1
    for i in wholeuser2:
        potential_collectnum = Collect.query.filter(Collect.user_id == i).count()
        if video_common[i] != 0:
            video_common[i] = video_common[i] / (math.sqrt(potential_collectnum * collect_num))
    print(user_common)
    print(video_common)
    alpha = 0.5
    for i in user_common:
        for j in video_common:
            if i == j:
                final[i] = alpha * user_common[i] + (1 - alpha) * video_common[i]
    print(final)
    sortedData = dict(sorted(final.items(), key=lambda data: data[1], reverse=True))
    user_pool=[]
    recommend_video_calculate={}
    for i in sortedData:
        if sortedData[i]>0:
            user_pool.append(i)
    if len(user_pool)>4:
        user_pool=user_pool[0:4:1]
    for k in user_pool:
        collect_this = Collect.query.filter(Collect.user_id == k)
        for item in collect_this:
            if item.video_id not in recommend_video_calculate.keys():
                recommend_video_calculate[item.video_id]= 0
            recommend_video_calculate[item.video_id] = recommend_video_calculate[item.video_id] + 1*sortedData[k]
    final_sorted_data= dict(sorted(recommend_video_calculate.items(),key=lambda data: data[1], reverse=True))
    final_sorted_data2= dict(sorted(recommend_video_calculate.items(),key=lambda data: data[1], reverse=True))
    recommend_item=[]
    for i in final_sorted_data2:
        for k in data3:
            if i == k.video_id:
                final_sorted_data.pop(i)
    for i in final_sorted_data:
        video_recommend = video.query.filter(video.id == i).first()
        video_item = Recommend_video(
            id = i,
            name= video_recommend.name,
            iurl= video_recommend.iurl,
            watch_num= video_recommend.watchnum,
            collect_num= video_recommend.real_collectnum,
            comment_num= video_recommend.collectnum,
            video_type= video_recommend.videotype,
            info= video_recommend.info
        )
        recommend_item.append(video_item)
    if len(recommend_item)>5:
        recommend_item=recommend_item[0:5:1]
    return render_template("home/recommend_video.html", data2=recommend_item)




@home.route('/love_add/', methods=['GET'])
@user_login_req
def love_add():
    mid = request.args.get('mid', '')
    user = UserInfo.query.filter(UserInfo.username == session["user"]).first()
    user2 = UserInfo.query.filter(UserInfo.user_id == int(mid)).first()
    usercol = User_relation.query.filter_by(
        be_id=int(mid),
        love_id=int(user.user_id)
    ).count()
    if usercol == 1:
        # 已收藏
        data = dict(ok=0)
    if usercol == 0:
        # 未收藏
        love = User_relation(
            be_id=int(mid),
            love_id=int(user.user_id)
        )
        db.session.add(love)
        db.session.commit()
        user.love_num = user.love_num + 1
        db.session.add(user)
        db.session.commit()
        user2.fan = user2.fan + 1
        db.session.add(user2)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)


@home.route('/love_user/<int:page>/', methods=["GET", "POST"])
@user_login_req
def love_user(page=None):
    user = UserInfo.query.filter(UserInfo.username == session["user"]).first()
    if page is None:
        page = 1
    data = UserInfo.query.join(User_relation, UserInfo.user_id == User_relation.be_id).filter(
        User_relation.love_id == user.user_id,
    ).order_by(User_relation.addtime.desc()).paginate(page=page, per_page=5)
    return render_template("home/love_user.html", data=data)


