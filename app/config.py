import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SECRET_KEY = os.getenv("SECRET_KEY")  # חובה להגדיר בשרת (systemd / env)
UPLOAD_PASSWORD = os.getenv("UPLOAD_PASSWORD")  # חובה להגדיר בשרת

UPLOAD_FOLDER = os.path.join(BASE_DIR, "images")

DATABASE_URL = os.getenv("DATABASE_URL")  # חובה להגדיר בשרת
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False

CORS_ORIGINS = [
    "https://zichron-olam.web.app",
    "https://zichron-olam.firebaseapp.com",
    "https://rashi63.com",
    "https://server.rashi63.com",
    "http://localhost:5173",
    "http://localhost:3000",
]
