from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField, FloatField
from wtforms.validators import DataRequired, URL


class RegisterForm(FlaskForm):
    fname = StringField("First Name", validators=[DataRequired()])
    lname = StringField("Last Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("LET ME IN!")


class CaloriesForm(FlaskForm):
    exercise = StringField("What did you do?", validators=[DataRequired()])
    gender = StringField("Gender", validators=[DataRequired()])
    weight = FloatField("Weight in Kgs", validators=[DataRequired()])
    height = FloatField("Height in cm", validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    submit = SubmitField("Check Burned Calories")
