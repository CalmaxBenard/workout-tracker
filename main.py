from datetime import date, datetime
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from forms import RegisterForm, LoginForm, CaloriesForm
import os
import smtplib
import requests

NUTRITIONIX_ENDPOINT = "https://trackapi.nutritionix.com/v2/natural/exercise"
NUTRITIONIX_APP_ID = os.environ.get("APP_ID")
NUTRITIONIX_APP_KEY = os.environ.get("APP_KEY")

nutritionix_headers = {
    "x-app-id": NUTRITIONIX_APP_ID,
    "x-app-key": NUTRITIONIX_APP_KEY,
    "content-type": "application/json",
}


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
ckeditor = CKEditor
Bootstrap5(app)

# Configure flask-login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy()
db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # check if users exists in the database
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if user:
            flash("That email is already registered, log in instead!")
            return redirect(url_for("login"))
        hashed_and_salted_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )
        new_user = User(
            first_name=form.fname.data,
            last_name=form.lname.data,
            email=form.email.data,
            password=hashed_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("calories"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check user email and password
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("You entered wrong password, please try again.")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("calories"))
    return render_template("login.html", form=form, current_user=current_user)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/calories", methods=["GET", "POST"])
def calories():
    form = CaloriesForm()
    if form.validate_on_submit():
        exercise = form.exercise.data
        gender = form.gender.data
        weight = form.weight.data
        height = form.height.data
        age = form.age.data
        nutritionix_data = {
            "query": exercise,
            "gender": gender,
            "weight_kg": weight,
            "height_cm": height,
            "age": age
        }
        response = requests.post(NUTRITIONIX_ENDPOINT, headers=nutritionix_headers, json=nutritionix_data).json()
        # response.raise_for_status()
        data = response["exercises"][0]
        # print(data)
        return render_template("calories.html", data=data, form=form, is_check=True)
    return render_template("calories.html", form=form, current_user=current_user, is_check=False)


if __name__ == "__main__":
    app.run(debug=True)
