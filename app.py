import logging

from flask import Flask
from flask_login import LoginManager, current_user

from database import Database, Record
from routes import ROUTES

app: Flask = Flask(
    __name__,
    template_folder="routes/templates",
    static_folder="routes/static"
)

def custom_templating():
    return dict(
        current_user = current_user,
        logged_in = not current_user.is_anonymous,
    )

app.context_processor(custom_templating)
app.logger.setLevel(logging.INFO)

app.config["SECRET_KEY"] = "abcdefg"
app.config["DEBUG"] = False

app.config.testing = False
app.config.db = Database()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(account_id):
    current_user: Record = app.config.db.fetch("SELECT * FROM accounts WHERE account_id=?", (account_id,))

    if current_user:
        return current_user[0].to_user()

for router in ROUTES:
    app.register_blueprint(router)
