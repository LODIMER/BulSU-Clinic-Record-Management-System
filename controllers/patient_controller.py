from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from controllers.decorators import staff_required
from models.activity_log import ActivityLogModel
from models.appointment import AppointmentModel
from models.clinic_visit import ClinicVisitModel
from models.patient import PatientModel
from services.gform_import import parse_gform_csv

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

        if not data["student_id"] or not data["first_name"] or not data["last_name"]:
            flash("Student ID, first name, and last name are required.", "danger")
            return render_template("staff/patients/form.html", patient=None)

        patient_id = PatientModel.create(data)
        ActivityLogModel.log(
            session["user_id"],
            "Added patient record",
            f"Patient ID: {patient_id}, Student: {data['student_id']}",
        )
        flash("Patient record created successfully.", "success")
        return redirect(url_for("patients.view_patient", patient_id=patient_id))

    return render_template("staff/patients/form.html", patient=None)


@patient_bp.route("/import", methods=["GET", "POST"])
@staff_required
def import_gform():
    if request.method == "POST":
        file = request.files.get("csv_file")
        if not file or not file.filename:
            flash("Please select a CSV file exported from Google Forms.", "danger")
            return render_template("staff/patients/import.html")

        if not file.filename.lower().endswith(".csv"):
            flash("Only CSV files are supported. Export responses from Google Sheets.", "danger")
            return render_template("staff/patients/import.html")

        update_existing = request.form.get("update_existing") == "1"
        parsed = parse_gform_csv(file.read())

        if not parsed["rows"]:
            for err in parsed["errors"]:
                flash(err, "warning")
            flash("No valid rows found in the CSV file.", "danger")
            return render_template(
                "staff/patients/import.html",
                preview=None,
                headers=parsed.get("headers"),
                mapping=parsed.get("mapping"),
            )

        stats = PatientModel.import_rows(parsed["rows"], update_existing=update_existing)

        ActivityLogModel.log(
            session["user_id"],
            "Imported Google Form responses",
            f"Imported: {stats['imported']}, Updated: {stats['updated']}, Skipped: {stats['skipped']}",
        )

        flash(
            f"Import complete — {stats['imported']} added, "
            f"{stats['updated']} updated, {stats['skipped']} skipped.",
            "success",
        )
        for err in parsed["errors"] + stats["errors"]:
            flash(err, "warning")

        return redirect(url_for("patients.list_patients"))

    return render_template("staff/patients/import.html")


@patient_bp.route("/<int:patient_id>")
@staff_required
def view_patient(patient_id):
    patient = PatientModel.get_by_id(patient_id)
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("patients.list_patients"))

    visits = ClinicVisitModel.get_by_patient(patient_id)
    appointments = AppointmentModel.get_by_patient(patient_id)
    return render_template(
        "shared/patient_detail.html",
        patient=patient,
        visits=visits,
        appointments=appointments,
        readonly=False,
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
