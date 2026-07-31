from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated


def staff_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if session.get("role") != "staff":
            flash("Access denied. Staff only.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)

    return decorated


def patient_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if session.get("role") != "patient":
            flash("Access denied.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)

    return decorated
