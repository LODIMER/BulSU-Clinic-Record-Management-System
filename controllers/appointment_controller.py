from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from controllers.decorators import staff_required
from models.activity_log import ActivityLogModel
from models.appointment import AppointmentModel
from models.patient import PatientModel

appointment_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@appointment_bp.route("/")
@staff_required
def list_appointments():
    search = request.args.get("search", "")
    status = request.args.get("status", "")
    appointments = AppointmentModel.get_all(search, status)
    return render_template(
        "staff/appointments/list.html",
        appointments=appointments,
        search=search,
        status=status,
    )


@appointment_bp.route("/add", methods=["GET", "POST"])
@staff_required
def add_appointment():
    patients = PatientModel.get_all()

    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        data = {
            "appointment_date": request.form.get("appointment_date", "").strip(),
            "appointment_time": request.form.get("appointment_time", "").strip(),
            "reason": request.form.get("reason", "").strip(),
        }

        if not patient_id or not all(data.values()):
            flash("All fields are required.", "danger")
            return render_template("staff/appointments/form.html", patients=patients)

        appointment_id = AppointmentModel.create(int(patient_id), data)
        AppointmentModel.update_status(appointment_id, "approved")
        ActivityLogModel.log(
            session["user_id"],
            "Created appointment",
            f"Appointment ID: {appointment_id}",
        )
        flash("Appointment created.", "success")
        return redirect(url_for("appointments.list_appointments"))

    return render_template("staff/appointments/form.html", patients=patients)


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
@staff_required
def cancel_appointment(appointment_id):
    appointment = AppointmentModel.get_by_id(appointment_id)
    if not appointment:
        flash("Appointment not found.", "danger")
        return redirect(url_for("appointments.list_appointments"))

    AppointmentModel.update_status(appointment_id, "cancelled")
    ActivityLogModel.log(
        session["user_id"],
        "Cancelled appointment",
        f"Appointment ID: {appointment_id}",
    )
    flash("Appointment cancelled.", "info")
    return redirect(url_for("appointments.list_appointments"))
