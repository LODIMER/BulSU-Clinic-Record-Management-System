from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from controllers.decorators import login_required, patient_required, staff_required
from models.activity_log import ActivityLogModel
from models.appointment import AppointmentModel
from models.patient import PatientModel

appointment_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@appointment_bp.route("/")
@login_required
def list_appointments():
    if session.get("role") == "staff":
        search = request.args.get("search", "")
        status = request.args.get("status", "")
        appointments = AppointmentModel.get_all(search, status)
        return render_template(
            "staff/appointments/list.html",
            appointments=appointments,
            search=search,
            status=status,
        )

    patient = PatientModel.get_by_user_id(session["user_id"])
    if not patient:
        flash("No patient profile found.", "warning")
        return redirect(url_for("dashboard.index"))

    appointments = AppointmentModel.get_by_patient(patient["id"])
    return render_template("patient/appointments.html", appointments=appointments)


@appointment_bp.route("/request", methods=["GET", "POST"])
@patient_required
def request_appointment():
    patient = PatientModel.get_by_user_id(session["user_id"])
    if not patient:
        flash("No patient profile found.", "warning")
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        data = {
            "appointment_date": request.form.get("appointment_date", "").strip(),
            "appointment_time": request.form.get("appointment_time", "").strip(),
            "reason": request.form.get("reason", "").strip(),
        }

        if not all(data.values()):
            flash("All fields are required.", "danger")
            return render_template("patient/request_appointment.html")

        appointment_id = AppointmentModel.create(patient["id"], data)
        ActivityLogModel.log(
            session["user_id"],
            "Submitted appointment request",
            f"Appointment ID: {appointment_id}",
        )
        flash("Appointment request submitted.", "success")
        return redirect(url_for("appointments.list_appointments"))

    return render_template("patient/request_appointment.html")


@appointment_bp.route("/<int:appointment_id>/status", methods=["POST"])
@staff_required
def update_status(appointment_id):
    status = request.form.get("status")
    staff_notes = request.form.get("staff_notes", "")
    valid = ("approved", "rejected", "completed", "cancelled")

    if status not in valid:
        flash("Invalid status.", "danger")
    else:
        AppointmentModel.update_status(appointment_id, status, staff_notes)
        ActivityLogModel.log(
            session["user_id"],
            f"Updated appointment status to {status}",
            f"Appointment ID: {appointment_id}",
        )
        flash(f"Appointment marked as {status}.", "success")

    return redirect(url_for("appointments.list_appointments"))


@appointment_bp.route("/<int:appointment_id>/reschedule", methods=["POST"])
@staff_required
def reschedule(appointment_id):
    appointment_date = request.form.get("appointment_date")
    appointment_time = request.form.get("appointment_time")

    if appointment_date and appointment_time:
        AppointmentModel.reschedule(appointment_id, appointment_date, appointment_time)
        ActivityLogModel.log(
            session["user_id"],
            "Rescheduled appointment",
            f"Appointment ID: {appointment_id}",
        )
        flash("Appointment rescheduled.", "success")
    else:
        flash("Date and time are required.", "danger")

    return redirect(url_for("appointments.list_appointments"))


@appointment_bp.route("/<int:appointment_id>/cancel", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    appointment = AppointmentModel.get_by_id(appointment_id)
    if not appointment:
        flash("Appointment not found.", "danger")
        return redirect(url_for("appointments.list_appointments"))

    if session.get("role") == "patient":
        patient = PatientModel.get_by_user_id(session["user_id"])
        if not patient or patient["id"] != appointment["patient_id"]:
            flash("Access denied.", "danger")
            return redirect(url_for("appointments.list_appointments"))

    AppointmentModel.update_status(appointment_id, "cancelled")
    ActivityLogModel.log(
        session["user_id"],
        "Cancelled appointment",
        f"Appointment ID: {appointment_id}",
    )
    flash("Appointment cancelled.", "info")
    return redirect(url_for("appointments.list_appointments"))
