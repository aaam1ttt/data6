from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from functools import wraps
from ..models.users import (
    list_users, create_user, delete_user, set_password, count_admins
)

bp = Blueprint("admin", __name__)

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        u = session.get("user")
        if not u or not u.get("is_admin"):
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

@bp.route("/users", methods=["GET"])
@login_required
@admin_required
def users_page():
    users = list_users()
    return render_template("admin_users.html", title="Пользователи", users=users)

@bp.route("/users/create", methods=["POST"])
@login_required
@admin_required
def users_create():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    is_admin = True if request.form.get("is_admin") == "on" else False
    if not username or not password:
        flash("Заполни логин и пароль", "error")
        return redirect(url_for("admin.users_page"))
    if not create_user(username, password, is_admin=is_admin):
        flash("Не удалось создать (логин уже занят?)", "error")
        return redirect(url_for("admin.users_page"))
    flash("Пользователь создан", "success")
    return redirect(url_for("admin.users_page"))

@bp.route("/users/<int:user_id>/reset_password", methods=["POST"])
@login_required
@admin_required
def users_reset_password(user_id: int):
    new_password = (request.form.get("new_password") or "").strip()
    if not new_password:
        flash("Укажи новый пароль", "error")
        return redirect(url_for("admin.users_page"))
    if set_password(user_id, new_password):
        flash("Пароль установлен", "success")
    else:
        flash("Не удалось обновить пароль", "error")
    return redirect(url_for("admin.users_page"))

@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def users_delete(user_id: int):
    if count_admins() <= 1:
        flash("Нельзя удалить последнего администратора", "error")
        return redirect(url_for("admin.users_page"))
    if delete_user(user_id):
        flash("Пользователь удалён", "success")
    else:
        flash("Не удалось удалить пользователя", "error")
    return redirect(url_for("admin.users_page"))
