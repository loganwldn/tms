from flask import Blueprint, render_template, current_app
from flask_login import login_required

home_router = Blueprint("home", __name__)

@home_router.route("/")
def index():
    tickets = current_app.config.db.fetch("SELECT * FROM tickets")

    for ticket in tickets:
        owner = current_app.config.db.fetch(
            "SELECT * FROM accounts WHERE account_id=?",
            (ticket.ticket_owner_id,)
        )

        if owner:
            ticket.owner = owner[0]

    return render_template("index.html", tickets=tickets)

@home_router.route("/account")
@login_required
def account():
    return render_template("account.html")
