from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from controllers.decorators import login_required, staff_required
from models.activity_log import ActivityLogModel
from models.user import UserModel

activity_bp = Blueprint("activities", __name__, url_prefix="/activities")
staff_bp = Blueprint("staff_mgmt", __name__, url_prefix="/staff")


@activity_bp.route("/")
@login_required
def list_activities():
    if session.get("role") == "staff":
        activities = ActivityLogModel.get_all(100)
        return render_template("staff/activities.html", activities=activities)

    activities = ActivityLogModel.get_by_user(session["user_id"], 50)
    return render_template("patient/activities.html", activities=activities)


@staff_bp.route("/")
@staff_required
def list_staff():
    staff_list = UserModel.get_all_staff()
    return render_template("staff/staff_mgmt/list.html", staff_list=staff_list)


@staff_bp.route("/add", methods=["GET", "POST"])
@staff_required
def add_staff():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("staff/staff_mgmt/form.html")

        try:
            user_id = UserModel.create(username, password, "staff")
            ActivityLogModel.log(
                session["user_id"],
                "Created staff account",
                f"Staff ID: {user_id}, Username: {username}",
            )
            flash("Staff account created.", "success")
            return redirect(url_for("staff_mgmt.list_staff"))
        except Exception:
            flash("Username already exists.", "danger")

    return render_template("staff/staff_mgmt/form.html")


@staff_bp.route("/<int:user_id>/reset-password", methods=["POST"])
@staff_required
def reset_password(user_id):
    new_password = request.form.get("new_password", "")
    if not new_password:
        flash("New password is required.", "danger")
    else:
        UserModel.reset_password(user_id, new_password)
        ActivityLogModel.log(
            session["user_id"],
            "Reset user password",
            f"User ID: {user_id}",
        )
        flash("Password reset successfully.", "success")
    return redirect(url_for("staff_mgmt.list_staff"))


@staff_bp.route("/<int:user_id>/toggle", methods=["POST"])
@staff_required
def toggle_staff(user_id):
    is_active = request.form.get("is_active") == "1"
    UserModel.toggle_active(user_id, is_active)
    ActivityLogModel.log(
        session["user_id"],
        "Toggled staff account status",
        f"User ID: {user_id}, Active: {is_active}",
    )
    flash("Staff account updated.", "success")
    return redirect(url_for("staff_mgmt.list_staff"))
