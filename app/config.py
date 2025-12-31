import os

# בסיס הפרויקט: /home/ubuntu/flaskapp
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    # ===== Security =====
    SECRET_KEY = os.getenv("SECRET_KEY")  # חובה בשרת
    UPLOAD_PASSWORD = os.getenv("UPLOAD_PASSWORD")  # חובה בשרת

    # ===== Uploads =====
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "images")

    # ===== Database =====
    DATABASE_URL = os.getenv("DATABASE_URL")  # חובה בשרת
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ===== CORS =====
    CORS_ORIGINS = [
        "https://zichron-olam.web.app",
        "https://zichron-olam.firebaseapp.com",
        "https://rashi63.com",
        "https://server.rashi63.com",
        "http://localhost:5173",
        "http://localhost:3000",
    ]
