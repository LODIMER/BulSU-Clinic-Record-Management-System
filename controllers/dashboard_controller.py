from flask import Blueprint, render_template

from controllers.decorators import staff_required
from models.appointment import AppointmentModel
from models.clinic_visit import ClinicVisitModel
from models.medicine import MedicineModel
from models.patient import PatientModel
from models.activity_log import ActivityLogModel

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@staff_required
def index():
    data = {
        "total_patients": PatientModel.count(),
        "today_appointments": AppointmentModel.get_today_count(),
        "total_visits": ClinicVisitModel.count(),
        "pending_submissions": ClinicVisitModel.count_pending(),
        "medicines": MedicineModel.get_all(),
        "low_stock": MedicineModel.get_low_stock(),
        "expired": MedicineModel.get_expired(),
        "recent_activities": ActivityLogModel.get_all(10),
        "recent_visits": ClinicVisitModel.get_recent(5),
    }
    return render_template("staff/dashboard.html", **data)
