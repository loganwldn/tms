from flask import Flask
from flask_login import LoginManager

from database import Database, Record
from routes import ROUTES

app: Flask = Flask(
    __name__,
    template_folder="routes/templates",
    static_folder="routes/static"
)

app.config["SECRET_KEY"] = "abcdefg"
app.config.db = Database()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(account_id):
    current_user: Record = app.config.db.fetch("SELECT * FROM accounts WHERE account_id=?", (account_id,))[0]
    
    return current_user.to_user()

for router in ROUTES:
    app.register_blueprint(router)
