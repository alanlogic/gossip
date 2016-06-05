from wtforms import Form, TextField, PasswordField, BooleanField, validators
from werkzeug.security import check_password_hash
from model import User, Player
from database import db_session


class LoginForm(Form):
    username = TextField('用户名', [validators.Required()])
    password = PasswordField('密码', [validators.Required()])

    def validate_username(self, field):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError('不存在的用户')
        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('密码错误')

    def get_user(self):
        return (User.query.filter(User.username == self.username.data)
                .one_or_none())


class RegisterForm(Form):
    username = TextField('用户名', [
        validators.Required(),
        validators.Length(min=6, max=20)
    ])
    email = TextField('Email', [
        validators.Required()
    ])
    password = PasswordField('密码', [
        validators.Length(min=6, max=20),
        validators.EqualTo('confirm', message='两次密码不匹配')
    ])
    confirm = PasswordField('重复密码')
    accept = BooleanField('接受协议', [validators.Required()])

    def add_user(self):
        user = User(self)
        db_session.add(user)
        # there should be improved to ensure User and Player have same user_id
        db_session.add(Player(nickname=self.username.data))
        db_session.commit()
        return user
