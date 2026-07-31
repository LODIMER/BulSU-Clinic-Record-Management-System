from models.activity_log import ActivityLogModel
from models.clinic_visit import ClinicVisitModel
from models.patient import PatientModel


REQUIRED_FIELDS = (
    "student_id",
    "first_name",
    "last_name",
    "course",
    "year_level",
    "visit_date",
    "visit_time",
    "reason",
    "symptoms",
)


def validate_student_form(form):
    errors = []
    for field in REQUIRED_FIELDS:
        if not form.get(field, "").strip():
            label = field.replace("_", " ").title()
            errors.append(f"{label} is required.")
    return errors


def process_student_visit_form(form):
    """
    Save student clinic visit form data:
    - create or update patient record (no login account)
    - create clinic visit record for staff review
    """
    errors = validate_student_form(form)
    if errors:
        return None, errors

    patient_data = {
        "student_id": form["student_id"].strip(),
        "first_name": form["first_name"].strip(),
        "last_name": form["last_name"].strip(),
        "course": form.get("course", "").strip(),
        "year_level": form.get("year_level", "").strip(),
        "contact_number": form.get("contact_number", "").strip(),
        "emergency_contact": form.get("emergency_contact", "").strip(),
        "medical_history": form.get("medical_history", "").strip(),
        "allergies": form.get("allergies", "").strip(),
    }

    patient_id = PatientModel.find_or_update_from_form(patient_data)

    visit_data = {
        "patient_id": patient_id,
        "visit_date": form["visit_date"].strip(),
        "visit_time": form["visit_time"].strip(),
        "reason": form["reason"].strip(),
        "symptoms": form["symptoms"].strip(),
    }

    visit_id = ClinicVisitModel.create_student_submission(visit_data)

    ActivityLogModel.log(
        None,
        "Student clinic visit form submitted",
        f"Visit ID: {visit_id}, Student ID: {patient_data['student_id']}",
    )

    return visit_id, []
