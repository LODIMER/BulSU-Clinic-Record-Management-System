from datetime import date

from flask import Blueprint, render_template, session

from controllers.decorators import login_required
from models.appointment import AppointmentModel
from models.clinic_visit import ClinicVisitModel
from models.medicine import MedicineModel
from models.patient import PatientModel
from models.activity_log import ActivityLogModel

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    role = session.get("role")

    if role == "staff":
        data = {
            "total_patients": PatientModel.count(),
            "today_appointments": AppointmentModel.get_today_count(),
            "total_visits": ClinicVisitModel.count(),
            "medicines": MedicineModel.get_all(),
            "low_stock": MedicineModel.get_low_stock(),
            "expired": MedicineModel.get_expired(),
            "recent_activities": ActivityLogModel.get_all(10),
            "recent_visits": ClinicVisitModel.get_recent(5),
        }
        return render_template("staff/dashboard.html", **data)

    patient = PatientModel.get_by_user_id(session["user_id"])
    if not patient:
        return render_template("patient/dashboard.html", patient=None)

    appointments = AppointmentModel.get_by_patient(patient["id"])
    visits = ClinicVisitModel.get_by_patient(patient["id"])
    upcoming = [a for a in appointments if a["status"] in ("pending", "approved")][:3]

    data = {
        "patient": patient,
        "upcoming_appointments": upcoming,
        "recent_visit": visits[0] if visits else None,
        "appointments": appointments[:5],
    }
    return render_template("patient/dashboard.html", **data)
