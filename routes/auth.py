from flask import Blueprint, current_app, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

auth_router = Blueprint(
    "auth", __name__,
    template_folder="templates/auth",
    url_prefix="/auth"
)

@auth_router.route("/login", methods=["GET", "POST"])
def login():
    if not current_user.is_anonymous:
        return redirect(url_for("home.account"))

    if request.method == "GET":
        return render_template("auth.html")

    username = request.form.get("username")
    password = request.form.get("password")

    existing_user = current_app.config.db.fetch("SELECT * FROM accounts WHERE username=?", (username,))

    if not existing_user or not check_password_hash(existing_user[0].password, password):
        flash("Login details incorrect!")
        return redirect(url_for("auth.login"))
    
    login_user(existing_user[0].to_user(), remember=False)
    return redirect(url_for("home.account"))

@auth_router.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth.html")
    
    username = request.form.get("username")
    password = request.form.get("password")

    existing_username = current_app.config.db.fetch("SELECT * FROM accounts WHERE username=?", (username,))

    if existing_username:
        flash("Username already exists!")
        return redirect(url_for("auth.signup"))
    
    current_app.config.db.execute(
        "INSERT INTO accounts (username, password, account_type) VALUES (?,?,'user')",
        (username, generate_password_hash(password, method="pbkdf2:sha256"))
    )

    return redirect(url_for("auth.login"))

@auth_router.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home.index"))