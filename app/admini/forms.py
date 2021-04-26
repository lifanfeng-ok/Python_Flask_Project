from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.model import Admini


class LoginForm(FlaskForm):
    """
    管理员登录表单
    """
    account = StringField(
        label="账号",
        validators=[
            DataRequired("账号不能为空")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！",
            # 注释此处显示forms报错errors信息
            # "required": "required"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("密码不能为空")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
            # 注释此处显示forms报错errors信息
            # "required": "required"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )

    def validate_account(self, field):
        account = field.data
        admin = Admini.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("账号不存在! ")


class Videoform(FlaskForm):
    title = StringField(
        label="视频名称",
        validators=[
            DataRequired("片名不能为空！")
        ],
        description="片名",
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入视频名称！"
        }
    )
    url = FileField(
        label="链接",
        validators=[
            DataRequired("请上传视频")
        ],
        description="视频链接",
    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("简介不能为空！")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": 5
        }
    )
    logo = FileField(
        label="封面",
        validators=[
            DataRequired("请上传封面！")
        ],
        description="封面",
    )
    # 标签要在数据库中查询已存在的标签
    type = SelectField(
        label="类别",
        validators=[
            DataRequired("请选择视频类别！")
        ],
        coerce=str,
        # 通过列表生成器生成列表, 解决列表生成式 强制转换为list
        choices=list([("仰卧起坐", "仰卧起坐"), ("俯卧撑", "俯卧撑"), ("深蹲", "深蹲"), ("器械运动", "器械运动")]),
        description="标签",
        render_kw={
            "class": "form-control",
        }
    )
    submit = SubmitField(
        '添加',
        render_kw={
            "class": "btn btn-primary",
        }
    )


class Editform(FlaskForm):
    title = StringField(
        label="视频名称",
        validators=[
            DataRequired("片名不能为空！")
        ],
        description="视频名称",
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入视频名称！"
        }
    )
    url = FileField(
        label="链接",
        validators=[
            DataRequired("请上传视频")
        ],
        description="视频链接",
    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("简介不能为空！")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": 5
        }
    )
    logo = FileField(
        label="封面",
        validators=[
            DataRequired("请上传封面！")
        ],
        description="封面",
    )
    # 标签要在数据库中查询已存在的标签
    type = SelectField(
        label="类别",
        validators=[
            DataRequired("请选择视频类别！")
        ],
        coerce=str,
        # 通过列表生成器生成列表, 解决列表生成式 强制转换为list
        choices=list([("仰卧起坐", "仰卧起坐"), ("俯卧撑", "俯卧撑"), ("深蹲", "深蹲"), ("器械运动", "器械运动")]),
        description="标签",
        render_kw={
            "class": "form-control",
        }
    )
    submit = SubmitField(
        '修改',
        render_kw={
            "class": "btn btn-primary",
        }
    )
