# BulSU Clinic Record Management System

A web-based clinic record management system for Bulacan State University, built with **Python Flask** using the **MVC (Model-View-Controller)** architecture.

## Features

### Clinic Staff
- Login with username and password
- Create and manage student/patient accounts
- Manage staff accounts and reset passwords
- Full access to clinic records
- Dashboard with patient count, appointments, visits, inventory alerts
- Patient records (CRUD, search)
- Clinic visit / medical record management
- Appointment approval, rejection, rescheduling, completion
- Medicine inventory management with low-stock and expired alerts
- Reports (visits, patients, appointments, medicine usage)
- System activity log

### Student / Patient
- Login with personal account
- View personal clinic records and profile
- Request and track appointments
- View clinic visit history
- Cannot access other students' records or medicine inventory

## Project Structure (MVC)

```
BulSU-Clinic-Record-Management-System/
├── app.py                  # Application entry point
├── config.py               # Configuration
├── seed_data.py            # Demo data seeder
├── requirements.txt
├── models/                 # MODEL - Data layer
│   ├── database.py
│   ├── user.py
│   ├── patient.py
│   ├── appointment.py
│   ├── clinic_visit.py
│   ├── medicine.py
│   └── activity_log.py
├── controllers/            # CONTROLLER - Business logic & routes
│   ├── auth_controller.py
│   ├── dashboard_controller.py
│   ├── patient_controller.py
│   ├── visit_controller.py
│   ├── appointment_controller.py
│   ├── medicine_controller.py
│   ├── report_controller.py
│   └── activity_controller.py
└── views/                  # VIEW - UI templates & static files
    ├── templates/
    └── static/css/
```

## Setup & Run

1. **Install Python 3.10+**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Seed demo data**
   ```bash
   python seed_data.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser:** http://localhost:5000

## Demo Accounts

| Role    | Username  | Password    |
|---------|-----------|-------------|
| Staff   | staff     | staff123    |
| Student | student1  | student123  |
| Student | student2  | student123  |

## Technology Stack

- **Python 3** with **Flask** web framework
- **SQLite** database
- **Jinja2** HTML templates
- **Werkzeug** password hashing
- Role-based access control (staff / patient)
