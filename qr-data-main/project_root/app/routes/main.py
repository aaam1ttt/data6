from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from functools import wraps
from ..models.history import list_history_by_user, delete_history_by_user

bp = Blueprint("main", __name__)

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

@bp.route("/")
def home():
    user = session.get("user")
    return render_template("home.html", title="Главная", user=user)

@bp.route("/history", methods=["GET"])
@login_required
def history_page():
    u = session["user"]
    rows = list_history_by_user(u["id"], limit=300)
    return render_template("history.html", title="История", rows=rows)

@bp.route("/history/clear", methods=["POST"])
@login_required
def history_clear():
    u = session["user"]
    delete_history_by_user(u["id"])
    flash("История очищена", "success")
    return redirect(url_for("main.history_page"))