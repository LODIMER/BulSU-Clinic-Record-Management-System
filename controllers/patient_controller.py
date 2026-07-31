from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from controllers.decorators import login_required, patient_required, staff_required
from models.activity_log import ActivityLogModel
from models.appointment import AppointmentModel
from models.clinic_visit import ClinicVisitModel
from models.patient import PatientModel
from models.user import UserModel

patient_bp = Blueprint("patients", __name__, url_prefix="/patients")


@patient_bp.route("/")
@staff_required
def list_patients():
    search = request.args.get("search", "")
    patients = PatientModel.get_all(search)
    return render_template("staff/patients/list.html", patients=patients, search=search)


@patient_bp.route("/add", methods=["GET", "POST"])
@staff_required
def add_patient():
    if request.method == "POST":
        data = _extract_patient_form()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not data["student_id"] or not data["first_name"] or not data["last_name"]:
            flash("Student ID, first name, and last name are required.", "danger")
            return render_template("staff/patients/form.html", patient=None)

        user_id = None
        if username and password:
            try:
                user_id = UserModel.create(username, password, "patient")
            except Exception:
                flash("Username already exists.", "danger")
                return render_template("staff/patients/form.html", patient=None)

        patient_id = PatientModel.create(data, user_id)
        ActivityLogModel.log(
            session["user_id"],
            "Added patient record",
            f"Patient ID: {patient_id}, Student: {data['student_id']}",
        )
        flash("Patient record created successfully.", "success")
        return redirect(url_for("patients.view_patient", patient_id=patient_id))

    return render_template("staff/patients/form.html", patient=None)


@patient_bp.route("/<int:patient_id>")
@login_required
def view_patient(patient_id):
    patient = PatientModel.get_by_id(patient_id)
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("dashboard.index"))

    if session.get("role") == "patient":
        own = PatientModel.get_by_user_id(session["user_id"])
        if not own or own["id"] != patient_id:
            flash("You cannot access other patients' records.", "danger")
            return redirect(url_for("dashboard.index"))

    visits = ClinicVisitModel.get_by_patient(patient_id)
    appointments = AppointmentModel.get_by_patient(patient_id)
    return render_template(
        "shared/patient_detail.html",
        patient=patient,
        visits=visits,
        appointments=appointments,
        readonly=session.get("role") == "patient",
    )


@patient_bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
@staff_required
def edit_patient(patient_id):
    patient = PatientModel.get_by_id(patient_id)
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("patients.list_patients"))

    if request.method == "POST":
        data = _extract_patient_form()
        PatientModel.update(patient_id, data)
        ActivityLogModel.log(
            session["user_id"],
            "Updated patient record",
            f"Patient ID: {patient_id}",
        )
        flash("Patient record updated.", "success")
        return redirect(url_for("patients.view_patient", patient_id=patient_id))

    return render_template("staff/patients/form.html", patient=patient)


@patient_bp.route("/profile")
@patient_required
def my_profile():
    patient = PatientModel.get_by_user_id(session["user_id"])
    if not patient:
        flash("No patient profile linked to your account.", "warning")
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("patients.view_patient", patient_id=patient["id"]))


def _extract_patient_form():
    return {
        "student_id": request.form.get("student_id", "").strip(),
        "first_name": request.form.get("first_name", "").strip(),
        "last_name": request.form.get("last_name", "").strip(),
        "course": request.form.get("course", "").strip(),
        "year_level": request.form.get("year_level", "").strip(),
        "contact_number": request.form.get("contact_number", "").strip(),
        "emergency_contact": request.form.get("emergency_contact", "").strip(),
        "medical_history": request.form.get("medical_history", "").strip(),
        "allergies": request.form.get("allergies", "").strip(),
    }
