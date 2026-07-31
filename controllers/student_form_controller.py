from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from services.student_visit import process_student_visit_form

student_form_bp = Blueprint("student_form", __name__)


@student_form_bp.route("/student-visit", methods=["GET", "POST"])
def visit_form():
    if request.method == "POST":
        form_data = {
            "student_id": request.form.get("student_id", ""),
            "first_name": request.form.get("first_name", ""),
            "last_name": request.form.get("last_name", ""),
            "course": request.form.get("course", ""),
            "year_level": request.form.get("year_level", ""),
            "visit_date": request.form.get("visit_date", ""),
            "visit_time": request.form.get("visit_time", ""),
            "reason": request.form.get("reason", ""),
            "symptoms": request.form.get("symptoms", ""),
            "contact_number": request.form.get("contact_number", ""),
            "emergency_contact": request.form.get("emergency_contact", ""),
            "medical_history": request.form.get("medical_history", ""),
            "allergies": request.form.get("allergies", ""),
        }

        visit_id, errors = process_student_visit_form(form_data)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "public/student_visit_form.html",
                form=form_data,
                today=date.today().isoformat(),
            )

        return redirect(url_for("student_form.visit_success", visit_id=visit_id))

    return render_template(
        "public/student_visit_form.html",
        form={},
        today=date.today().isoformat(),
        now=datetime.now().strftime("%H:%M"),
    )


@student_form_bp.route("/student-visit/success")
def visit_success():
    visit_id = request.args.get("visit_id")
    return render_template("public/student_visit_success.html", visit_id=visit_id)
