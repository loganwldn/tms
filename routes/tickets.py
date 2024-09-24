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

    if current_app.config.testing:
        return "", 200

    return redirect(url_for("home.index"))

@tickets_router.route("/update", methods=["GET", "POST"])
@login_required
def update_ticket():
    if request.method == "GET":
        try:
            ticket_id = request.args.get("ticket_id")
        except TypeError:
            return redirect(url_for("home.index"))

        ticket = current_app.config.db.fetch(
            "SELECT * FROM tickets WHERE ticket_id=?",
            (ticket_id,)
        )

        if not ticket:
            return redirect(url_for("home.index"))

        return render_template("edit.html", ticket=ticket[0])

    ticket_id = request.form.get("ticket_id")
    new_title = request.form.get("title")
    new_content = request.form.get("content")
    last_updated = datetime.now()

    current_app.config.db.execute(
        "UPDATE tickets SET title=?, content=?, last_updated=? WHERE ticket_id=?",
        (new_title, new_content, last_updated, ticket_id)
    )

    if current_app.config.testing:
        return "", 200

    return redirect(url_for("tickets.display", ticket_id=ticket_id))

@tickets_router.route("/state", methods=["POST"])
@login_required
def set_ticket_state():
    ticket_id = request.form.get("ticket_id")
    ticket = current_app.config.db.fetch(
        "SELECT * FROM tickets WHERE ticket_id=?",
        (ticket_id,)
    )

    if not ticket or not current_user.is_admin or current_user.id != ticket[0].ticket_owner_id:
        return redirect(url_for("home.index"))

    ticket = ticket[0]
    
    current_app.config.db.execute(
        "UPDATE tickets SET is_open=? WHERE ticket_id=?",
        (not ticket.is_open, ticket_id)
    )

    if current_app.config.testing:
        return "", 200

    return redirect(url_for("home.index"))

@tickets_router.route("/delete", methods=["POST"])
@login_required
def delete_ticket():
    if not current_user.is_admin:
        return redirect(url_for("home.index"))

    ticket_id = request.form.get("ticket_id")

    current_app.config.db.execute(
        "DELETE FROM tickets WHERE ticket_id=?",
        (ticket_id,)
    )

    if current_app.config.testing:
        return "", 200

    return redirect(url_for("home.index"))