from datetime import date, datetime



from flask import Blueprint, flash, redirect, render_template, request, session, url_for



from controllers.decorators import staff_required

from models.activity_log import ActivityLogModel

from models.clinic_visit import ClinicVisitModel

from models.medicine import MedicineModel

from models.patient import PatientModel



visit_bp = Blueprint("visits", __name__, url_prefix="/visits")





@visit_bp.route("/")

@staff_required

def list_visits():

    search = request.args.get("search", "")

    visits = ClinicVisitModel.get_all(search)

    return render_template("staff/visits/list.html", visits=visits, search=search)





@visit_bp.route("/add", methods=["GET", "POST"])

@staff_required

def add_visit():

    patients = PatientModel.get_all()

    medicines = MedicineModel.get_all()



    if request.method == "POST":

        data = {

            "patient_id": request.form.get("patient_id"),

            "visit_date": request.form.get("visit_date", date.today().isoformat()),

            "visit_time": request.form.get("visit_time", datetime.now().strftime("%H:%M")),

            "reason": request.form.get("reason", "").strip(),

            "symptoms": request.form.get("symptoms", "").strip(),

            "vital_signs": request.form.get("vital_signs", "").strip(),

            "assessment": request.form.get("assessment", "").strip(),

            "treatment": request.form.get("treatment", "").strip(),

            "notes": request.form.get("notes", "").strip(),

        }



        if not data["patient_id"] or not data["reason"]:

            flash("Patient and reason for visit are required.", "danger")

            return render_template(

                "staff/visits/form.html",

                patients=patients,

                medicines=medicines,

                visit=None,

            )



        visit_id = ClinicVisitModel.create(data, session["user_id"])



        medicine_id = request.form.get("medicine_id")

        quantity = request.form.get("medicine_quantity", "0")

        if medicine_id and int(quantity) > 0:

            if not MedicineModel.release(visit_id, int(medicine_id), int(quantity)):

                flash("Visit recorded but medicine release failed (insufficient stock).", "warning")

            else:

                ActivityLogModel.log(

                    session["user_id"],

                    "Released medicine",

                    f"Visit ID: {visit_id}, Medicine ID: {medicine_id}, Qty: {quantity}",

                )



        ActivityLogModel.log(

            session["user_id"],

            "Recorded clinic visit",

            f"Visit ID: {visit_id}",

        )

        flash("Clinic visit recorded successfully.", "success")

        return redirect(url_for("visits.view_visit", visit_id=visit_id))



    return render_template(

        "staff/visits/form.html",

        patients=patients,

        medicines=medicines,

        visit=None,

    )





@visit_bp.route("/<int:visit_id>")

@staff_required

def view_visit(visit_id):

    visit = ClinicVisitModel.get_by_id(visit_id)

    if not visit:

        flash("Visit record not found.", "danger")

        return redirect(url_for("visits.list_visits"))



    medicines = ClinicVisitModel.get_medicines_for_visit(visit_id)

    pending = ClinicVisitModel.is_pending(visit)

    return render_template(

        "shared/visit_detail.html",

        visit=visit,

        medicines=medicines,

        pending=pending,

    )





@visit_bp.route("/<int:visit_id>/complete", methods=["GET", "POST"])

@staff_required

def complete_visit(visit_id):

    visit = ClinicVisitModel.get_by_id(visit_id)

    if not visit:

        flash("Visit record not found.", "danger")

        return redirect(url_for("visits.list_visits"))



    medicines = MedicineModel.get_all()



    if request.method == "POST":

        data = {

            "visit_date": request.form.get("visit_date", visit["visit_date"]),

            "visit_time": request.form.get("visit_time", visit["visit_time"]),

            "reason": request.form.get("reason", visit["reason"]).strip(),

            "symptoms": request.form.get("symptoms", visit.get("symptoms", "")).strip(),

            "vital_signs": request.form.get("vital_signs", "").strip(),

            "assessment": request.form.get("assessment", "").strip(),

            "treatment": request.form.get("treatment", "").strip(),

            "notes": request.form.get("notes", "").strip(),

        }



        if not data["reason"]:

            flash("Reason for visit is required.", "danger")

            return render_template(

                "staff/visits/complete.html",

                visit=visit,

                medicines=medicines,

            )



        ClinicVisitModel.update(visit_id, data, staff_id=session["user_id"])



        medicine_id = request.form.get("medicine_id")

        quantity = request.form.get("medicine_quantity", "0")

        if medicine_id and int(quantity) > 0:

            if not MedicineModel.release(visit_id, int(medicine_id), int(quantity)):

                flash("Visit updated but medicine release failed (insufficient stock).", "warning")

            else:

                ActivityLogModel.log(

                    session["user_id"],

                    "Released medicine",

                    f"Visit ID: {visit_id}, Medicine ID: {medicine_id}, Qty: {quantity}",

                )



        ActivityLogModel.log(

            session["user_id"],

            "Completed student visit submission",

            f"Visit ID: {visit_id}",

        )

        flash("Student visit record completed.", "success")

        return redirect(url_for("visits.view_visit", visit_id=visit_id))



    return render_template(

        "staff/visits/complete.html",

        visit=visit,

        medicines=medicines,

    )

