from controllers.auth_controller import auth_bp
from controllers.dashboard_controller import dashboard_bp
from controllers.patient_controller import patient_bp
from controllers.visit_controller import visit_bp
from controllers.appointment_controller import appointment_bp
from controllers.medicine_controller import medicine_bp
from controllers.report_controller import report_bp
from controllers.activity_controller import activity_bp, staff_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "patient_bp",
    "visit_bp",
    "appointment_bp",
    "medicine_bp",
    "report_bp",
    "activity_bp",
    "staff_bp",
]
