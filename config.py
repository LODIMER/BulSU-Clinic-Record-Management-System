import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "bulsu-clinic-secret-key-2026")
    DATABASE = os.path.join(BASE_DIR, "clinic.db")
    LOW_STOCK_THRESHOLD = 10
    SESSION_PERMANENT = False
