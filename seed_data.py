"""Seed the database with demo data for testing."""

from datetime import date, timedelta

from models.database import init_db
from models.user import UserModel
from models.patient import PatientModel
from models.appointment import AppointmentModel
from models.clinic_visit import ClinicVisitModel
from models.medicine import MedicineModel
from models.activity_log import ActivityLogModel


def seed():
    init_db()

    staff_id = UserModel.create("staff", "staff123", "staff")
    patient_user_id = UserModel.create("student1", "student123", "patient")
    patient2_user_id = UserModel.create("student2", "student123", "patient")

    patient1_id = PatientModel.create(
        {
            "student_id": "2021-00001",
            "first_name": "Juan",
            "last_name": "Dela Cruz",
            "course": "BS Information Technology",
            "year_level": "3rd Year",
            "contact_number": "09171234567",
            "emergency_contact": "Maria Dela Cruz - 09181234567",
            "medical_history": "None",
            "allergies": "Penicillin",
        },
        patient_user_id,
    )

    patient2_id = PatientModel.create(
        {
            "student_id": "2022-00042",
            "first_name": "Maria",
            "last_name": "Santos",
            "course": "BS Nursing",
            "year_level": "2nd Year",
            "contact_number": "09191234567",
            "emergency_contact": "Pedro Santos - 09201234567",
            "medical_history": "Asthma",
            "allergies": "None",
        },
        patient2_user_id,
    )

    today = date.today()
    AppointmentModel.create(
        patient1_id,
        {
            "appointment_date": today.isoformat(),
            "appointment_time": "09:00",
            "reason": "Annual physical checkup",
        },
    )
    AppointmentModel.create(
        patient2_id,
        {
            "appointment_date": (today + timedelta(days=3)).isoformat(),
            "appointment_time": "14:00",
            "reason": "Follow-up consultation",
        },
    )

    visit_id = ClinicVisitModel.create(
        {
            "patient_id": patient1_id,
            "visit_date": (today - timedelta(days=7)).isoformat(),
            "visit_time": "10:30",
            "reason": "Headache and fever",
            "vital_signs": "BP: 120/80, Pulse: 78, Temp: 37.5°C",
            "assessment": "Mild viral infection",
            "treatment": "Rest and hydration",
            "notes": "Advised to return if symptoms persist",
        },
        staff_id,
    )

    med1 = MedicineModel.create(
        {"name": "Paracetamol 500mg", "category": "Analgesic", "quantity": 200, "expiration_date": "2027-06-30"}
    )
    MedicineModel.create(
        {"name": "Ibuprofen 400mg", "category": "Anti-inflammatory", "quantity": 5, "expiration_date": "2026-12-31"}
    )
    MedicineModel.create(
        {"name": "Cetirizine 10mg", "category": "Antihistamine", "quantity": 50, "expiration_date": "2025-01-15"}
    )
    MedicineModel.create(
        {"name": "Amoxicillin 500mg", "category": "Antibiotic", "quantity": 80, "expiration_date": "2027-03-15"}
    )

    MedicineModel.release(visit_id, med1, 2)

    ActivityLogModel.log(staff_id, "Seeded demo database", "System initialization")

    print("Database seeded successfully!")
    print("Staff login:    staff / staff123")
    print("Student login:  student1 / student123")
    print("Student login:  student2 / student123")


if __name__ == "__main__":
    seed()