from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from controllers.decorators import staff_required
from models.activity_log import ActivityLogModel
from models.medicine import MedicineModel

medicine_bp = Blueprint("medicines", __name__, url_prefix="/medicines")


@medicine_bp.route("/")
@staff_required
def list_medicines():
    medicines = MedicineModel.get_all()
    low_stock = MedicineModel.get_low_stock()
    expired = MedicineModel.get_expired()
    return render_template(
        "staff/medicines/list.html",
        medicines=medicines,
        low_stock=low_stock,
        expired=expired,
    )


@medicine_bp.route("/add", methods=["GET", "POST"])
@staff_required
def add_medicine():
    if request.method == "POST":
        data = _extract_medicine_form()
        if not data["name"]:
            flash("Medicine name is required.", "danger")
            return render_template("staff/medicines/form.html", medicine=None)

        medicine_id = MedicineModel.create(data)
        ActivityLogModel.log(
            session["user_id"],
            "Added medicine",
            f"Medicine ID: {medicine_id}, Name: {data['name']}",
        )
        flash("Medicine added successfully.", "success")
        return redirect(url_for("medicines.list_medicines"))

    return render_template("staff/medicines/form.html", medicine=None)


@medicine_bp.route("/<int:medicine_id>/edit", methods=["GET", "POST"])
@staff_required
def edit_medicine(medicine_id):
    medicine = MedicineModel.get_by_id(medicine_id)
    if not medicine:
        flash("Medicine not found.", "danger")
        return redirect(url_for("medicines.list_medicines"))

    if request.method == "POST":
        data = _extract_medicine_form()
        MedicineModel.update(medicine_id, data)
        ActivityLogModel.log(
            session["user_id"],
            "Updated medicine",
            f"Medicine ID: {medicine_id}",
        )
        flash("Medicine updated.", "success")
        return redirect(url_for("medicines.list_medicines"))

    return render_template("staff/medicines/form.html", medicine=medicine)


@medicine_bp.route("/<int:medicine_id>/delete", methods=["POST"])
@staff_required
def delete_medicine(medicine_id):
    MedicineModel.delete(medicine_id)
    ActivityLogModel.log(
        session["user_id"],
        "Removed medicine",
        f"Medicine ID: {medicine_id}",
    )
    flash("Medicine removed.", "info")
    return redirect(url_for("medicines.list_medicines"))


def _extract_medicine_form():
    return {
        "name": request.form.get("name", "").strip(),
        "category": request.form.get("category", "").strip(),
        "quantity": request.form.get("quantity", "0"),
        "expiration_date": request.form.get("expiration_date", "").strip(),
    }
