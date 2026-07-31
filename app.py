import os

from flask import Flask

from config import Config
from controllers import (
    activity_bp,
    appointment_bp,
    auth_bp,
    dashboard_bp,
    medicine_bp,
    patient_bp,
    report_bp,
    staff_bp,
    visit_bp,
)
from models.database import init_db


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join("views", "templates"),
        static_folder=os.path.join("views", "static"),
    )
    app.config.from_object(Config)

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(visit_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(medicine_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(staff_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, host="0.0.0.0", port=5000)
