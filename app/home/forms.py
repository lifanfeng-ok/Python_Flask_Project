from wtforms import StringField, PasswordField, SubmitField, validators, IntegerField, TextAreaField, FileField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("学号: ", validators=[validators.DataRequired(message="请输入8位以数字组成的学号")],render_kw={"placeholder":"请输入用户名!",
            "required":'required' })
    password = PasswordField("密码: ", validators=[validators.DataRequired(), validators.Length(min=6, message="请输入至少6位数的密码")],render_kw={"placeholder":"请输入6位数以上的密码!",
            "required":'required' })
    submit = SubmitField("提交")

class Submit(FlaskForm):
    submit=SubmitField("+关注该用户",render_kw={"class":"btn btn-danger"})

class RegisterForm(FlaskForm):
    username = StringField("Username: ",[validators.DataRequired(message="You must input a valid username")],render_kw={"class":"kuang_txt phone","placeholder":"请输入用户名!", "required":'required'})
    phone = StringField("phone: ",validators=[validators.DataRequired(), validators.Length(min=9,max=9,message="请输入9位数手机号码")],render_kw={"class":"kuang_txt email","placeholder":"请输入9位手机号码!", "required":'required' })
    password = PasswordField("Password: ",[validators.DataRequired(),validators.Length(min=6,message="请输入6位数以上的密码")],render_kw={"class":"kuang_txt possword","placeholder":"请输入6位数以上密码!", "required":'required' })
    confirm = PasswordField("Confirm Password: ",[validators.EqualTo('password',message='密码不匹配')],render_kw={"class":"kuang_txt possword","placeholder":"请再次输入以上密码!", "required":'required' })
    submit = SubmitField("提交",render_kw={"class":"btn_zhuce"})

class EditForm(FlaskForm):
    username = StringField("用户名: ",[validators.DataRequired(message="You must input a valid username")],render_kw={"class":"form-control","placeholder":"请输入用户名!", "required":'required'})
    password = PasswordField("密码: ",[validators.DataRequired(),validators.Length(min=6,message="请输入6位数以上的密码")],render_kw={"class":"form-control","placeholder":"请输入6位数以上密码!", "required":'required' })
    confirm = PasswordField("确认密码: ", [validators.EqualTo('password', message='密码不匹配')],
                            render_kw={"class": "form-control", "placeholder": "请再次输入以上密码!",
                                       "required": 'required'})
    phone = StringField("手机号码: ", validators=[validators.DataRequired(), validators.Length(min=11,max=11,message="请输入11位数手机号码")],
                        render_kw={"class": "form-control", "placeholder": "请输入11位手机号码!", "required": 'required'})
    face = FileField(
        label="头像",
        validators=[
            DataRequired("请上传头像！")
        ],
        description="头像",
    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("简介不能为空！")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": 8
        }
    )
    submit = SubmitField("提交修改",render_kw={"class":"btn-primary form-control"})

class CommentForm(FlaskForm):
    content=TextAreaField( "内容: ",[validators.DataRequired(message="You must input a valid username")],
                           render_kw={"id":"input_content"}  )
    submit=SubmitField("提交评论",render_kw={"class":"btn btn-success","id":"btn-sub"})