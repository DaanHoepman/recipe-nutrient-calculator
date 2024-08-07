from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    username = StringField('Username',
                       id='username_login',
                       validators=[DataRequired()]
                       )
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()]
                             )
    
class CreateAccountForm(FlaskForm):
    full_name = StringField('Full_Name',
                       id='full_name_create',
                       )
    username = StringField('Username',
                           id='username_create',
                           validators=[DataRequired()]
                           )
    email = StringField('Email',
                        id='email_create',
                        validators=[DataRequired(), Email()]
                        )
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()]
                             )