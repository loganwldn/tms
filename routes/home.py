from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user

home_router = Blueprint("home", __name__)

@home_router.route("/")
def index():
    return render_template("index.html")

@home_router.route("/account")
@login_required
def account():
    return f"<p>Welcome, {current_user.username}</p>"