from flask import Blueprint, render_template

from controllers.decorators import staff_required
from models.appointment import AppointmentModel
from models.clinic_visit import ClinicVisitModel
from models.medicine import MedicineModel
from models.patient import PatientModel

report_bp = Blueprint("reports", __name__, url_prefix="/reports")


@report_bp.route("/")
@staff_required
def index():
    data = {
        "total_visits": ClinicVisitModel.count(),
        "total_patients": PatientModel.count(),
        "appointment_summary": AppointmentModel.status_summary(),
        "common_reasons": ClinicVisitModel.common_reasons(),
        "medicine_usage": MedicineModel.usage_summary(),
        "low_stock": MedicineModel.get_low_stock(),
        "expired": MedicineModel.get_expired(),
        "medicines": MedicineModel.get_all(),
    }
    return render_template("staff/reports.html", **data)
