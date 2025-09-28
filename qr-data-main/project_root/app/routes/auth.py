from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models.users import find_user_by_username, verify_password, touch_last_login
from ..models.history import delete_history_by_user
from datetime import datetime
from dateutil import parser  # если нет, установи python-dateutil; но мы обойдёмся без парсера

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        user = find_user_by_username(username)
        if not user or not verify_password(user["password_hash"], password):
            flash("Неверный логин или пароль", "error")
            return render_template("login.html", title="Вход")

        # авто-очистка истории, если не заходил > 10 дней
        last_login = user.get("last_login")
        if last_login:
            # last_login в SQLite формате 'YYYY-MM-DD HH:MM:SS'
            try:
                from datetime import datetime, timedelta
                last_dt = datetime.strptime(last_login, "%Y-%m-%d %H:%M:%S")
                if datetime.now() - last_dt > timedelta(days=10):
                    delete_history_by_user(user["id"])
            except Exception:
                pass

        touch_last_login(user["id"])
        session["user"] = {"id": user["id"], "username": user["username"], "is_admin": bool(user["is_admin"])}
        return redirect(url_for("main.home"))
    return render_template("login.html", title="Вход")

@bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("main.home"))