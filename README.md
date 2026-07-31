# BulSU Clinic Record Management System

A web-based clinic record management system for Bulacan State University, built with **Python Flask** using the **MVC (Model-View-Controller)** architecture.

## Features

### Clinic Staff
- Login with username and password
- Create and manage student/patient records
- Manage staff accounts and reset passwords
- Full access to clinic records
- Dashboard with patient count, appointments, visits, inventory alerts
- Review and complete student-submitted clinic visit forms
- Patient records (CRUD, search)
- Clinic visit / medical record management
- Appointment approval, rejection, rescheduling, completion
- Medicine inventory management with low-stock and expired alerts
- Reports (visits, patients, appointments, medicine usage)
- System activity log

### Student / Patient
- **No login account required**
- Fill out the **Student Clinic Visit Form** when visiting the clinic
- Information is saved directly to the clinic database
- Clinic staff review and manage submitted visit records
- Students cannot access the staff dashboard, other students' records, appointments, medicines, reports, or system activities

## Student Process

```
Student visits clinic → Fills out Student Clinic Visit Form → Submits form
→ Data saved to database → Clinic staff reviews submission → Staff completes visit record
```

## Project Structure (MVC)

```
BulSU-Clinic-Record-Management-System/
├── app.py                  # Application entry point
├── config.py               # Configuration
├── seed_data.py            # Demo data seeder
├── requirements.txt
├── models/                 # MODEL - Data layer
├── controllers/            # CONTROLLER - Business logic & routes
├── services/               # Business services
└── views/                  # VIEW - UI templates & static files
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

5. **Open in browser**
   - Staff login: http://localhost:5000/login
   - Student form: http://localhost:5000/student-visit

## Demo Account

| Role  | Username | Password  |
|-------|----------|-----------|
| Staff | staff    | staff123  |

Students do not have login accounts. Use the Student Clinic Visit Form at `/student-visit`.

## Technology Stack

- **Python 3** with **Flask** web framework
- **SQLite** database
- **Jinja2** HTML templates
- **Werkzeug** password hashing
- Staff-only access control
