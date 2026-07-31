from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from controllers.decorators import login_required
from models.activity_log import ActivityLogModel
from models.user import UserModel

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("login.html")

        user = UserModel.authenticate(username, password)
        if user:
            if user["role"] != "staff":
                flash(
                    "Students do not need to log in. Please use the Student Clinic Visit Form.",
                    "info",
                )
                return redirect(url_for("student_form.visit_form"))

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            ActivityLogModel.log(user["id"], "Logged in", f"User: {username}")
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("dashboard.index"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    user_id = session.get("user_id")
    username = session.get("username")
    ActivityLogModel.log(user_id, "Logged out", f"User: {username}")
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
