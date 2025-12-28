import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SECRET_KEY = os.getenv("SECRET_KEY", "wefklnsvcojhKJKfdsn")
UPLOAD_PASSWORD = os.getenv("UPLOAD_PASSWORD", "yoni1990")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "images")

CORS_ORIGINS = [
    "https://zichron-olam.web.app",
    "https://zichron-olam.firebaseapp.com",
    "https://rashi63.com",
    "https://server.rashi63.com",
    "http://localhost:5173",
    "http://localhost:3000",
]
