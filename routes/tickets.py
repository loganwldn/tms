from datetime import datetime

from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash
from flask_login import login_required, current_user

tickets_router = Blueprint(
    "tickets", __name__,
    url_prefix="/ticket",
    template_folder="templates/tickets"
)

@tickets_router.route("/<int:ticket_id>")
def display(ticket_id: int):
    ticket = current_app.config.db.fetch(
        "SELECT * FROM tickets WHERE ticket_id=?",
        (ticket_id,)
    )

    if not ticket:
        return redirect(url_for("home.index"))

    return render_template("view.html", ticket=ticket[0])

@tickets_router.route("/create", methods=["GET", "POST"])
@login_required
def create_ticket():
    if request.method == "GET":
        return render_template("create.html")

    title = request.form.get("title")
    content = request.form.get("content")
    posted_at = datetime.now()
    ticket_owner_id = current_user.id

    current_app.config.db.execute(
        "INSERT INTO tickets (ticket_owner_id, title, content, post_date) VALUES (?,?,?,?)",
        (ticket_owner_id, title, content, posted_at)
    )

    return redirect(url_for("home.index"))

@tickets_router.route("/delete", methods=["POST"])
@login_required
def delete_ticket():
    if not current_user.is_admin:
        return redirect(url_for("home.index"))

    ticket_id = request.form.get("ticket_id")

    print(f"delete {ticket_id}")
    current_app.config.db.execute(
        "DELETE FROM tickets WHERE ticket_id=?",
        (ticket_id,)
    )

    return redirect(url_for("home.index"))