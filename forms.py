from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, Length

#LOGIN
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=100)])
    submit = SubmitField("Login In!")

#REGISTER
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=100)])
    name = StringField("Name", validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField("Sign me up!")

class ClassForm(FlaskForm):
    day = SelectField(label="Day", choices=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
    from_hour = SelectField(label="From", choices=[(f"{i+7}", f"{value:02d}:00") for i, value in enumerate(range(7,23))])
    until_hour = SelectField(label="Until", choices=[(f"{i+7}", f"{value:02d}:00") for i, value in enumerate(range(7,23))])
    area = SelectField(label="Area", choices=['AH', 'AJ', 'DP', 'ED', 'EF', 'EL', 'EP', 'ER', 'FD', 'GC', 'PB', 'All'])
    comprobate = RadioField()
    
class ForgetUser(FlaskForm):
    user = StringField("User", validators=[DataRequired(), Length(min=6, max=100)])
    submit = SubmitField("Find me!")
    
class ForgetPassword(FlaskForm):
    new_password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=100)])
    submit = SubmitField("I'm ready!")