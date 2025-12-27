from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import io
import os
import time
from flask import session

PASSWORD = "yoni1990"


app = Flask(__name__)
app.secret_key = "wefklnsvcojhKJKfdsn"

# ------------------------------
#  הגדרת CORS ל-React
# ------------------------------
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://zichron-olam.web.app",
            "https://zichron-olam.firebaseapp.com",
            "https://rashi63.com",
            "https://server.rashi63.com",
            "http://localhost:5173",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "x-api-key"],
        "supports_credentials": True
    }
})

# ------------------------------
# תיקיית תמונות
# ------------------------------
UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("upload_ui"))
        else:
            return render_template("login.html", error="סיסמה שגויה")

    return render_template("login.html", error=None)


# ==========================================================
#        1) API להעלאה דרך React
# ==========================================================
@app.route("/upload", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    file = request.files["file"]

    # זיהוי סיומת
    file_bytes = file.read()
    try:
        img = Image.open(io.BytesIO(file_bytes))
        file_ext = img.format.lower()  # jpg / png / etc
    except Exception:
        return jsonify({"error": "Invalid image"}), 400

    file.stream.seek(0)

    # יצירת שם קובץ לפי timestamp
    timestamp = int(time.time())
    filename = f"{timestamp}.{file_ext}"

    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    return jsonify({"id": timestamp, "name": filename, "mimeType": f"image/{file_ext}"})


# ==========================================================
#        2) רשימת קבצים (React)
# ==========================================================
@app.route("/files", methods=["GET"])
def list_files():
    files = []
    for fname in os.listdir(UPLOAD_FOLDER):
        if "." not in fname:
            continue

        ts = fname.split(".")[0]
        if not ts.isdigit():
            continue

        files.append({
            "id": ts,
            "name": fname,
            "mimeType": f"image/{fname.split('.')[-1]}",
            "createdTime": ts
        })

    files_sorted = sorted(files, key=lambda x: int(x["id"]), reverse=True)
    return jsonify(files_sorted)


# ==========================================================
#        3) הצגת תמונה
# ==========================================================
@app.route("/files/<file_id>/content", methods=["GET"])
def serve_image(file_id):
    for fname in os.listdir(UPLOAD_FOLDER):
        if fname.startswith(file_id):
            return send_from_directory(UPLOAD_FOLDER, fname)
    return jsonify({"error": "File not found"}), 404


# ==========================================================
#        4) מחיקת תמונה
# ==========================================================
@app.route("/files/<file_id>", methods=["DELETE"])
def delete_image(file_id):
    deleted = False
    for fname in os.listdir(UPLOAD_FOLDER):
        if fname.startswith(file_id):
            os.remove(os.path.join(UPLOAD_FOLDER, fname))
            deleted = True

    if deleted:
        return ("", 204)
    return jsonify({"error": "File not found"}), 404


# ==========================================================
#        5) דף HTML עבור מובייל — העלאה ללא CORS
# ==========================================================
@app.route("/upload-ui", methods=["GET"])
def upload_ui():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("upload.html")


# ==========================================================
#        6) העלאה ישירה מה-HTML (מובייל)
# ==========================================================
@app.route("/upload-direct", methods=["POST"])
def upload_direct():
    if not session.get("logged_in"):
        return "לא מורשה", 401

    if "file" not in request.files:
        return "לא נבחר קובץ", 400

    file = request.files["file"]
    if file.filename == "":
        return "לא נבחר קובץ", 400

    file_bytes = file.read()
    try:
        img = Image.open(io.BytesIO(file_bytes))
        ext = img.format.lower()
    except Exception:
        return "זה לא קובץ תמונה תקין", 400

    file.stream.seek(0)

    timestamp = int(time.time())
    filename = f"{timestamp}.{ext}"

    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    return f"תמונה הועלתה בהצלחה! שם הקובץ: {filename}"


# ==========================================================
#        7) דף בית
# ==========================================================
@app.route("/")
def home():
    return "Flask server is running heidad!"


# ==========================================================
#        הפעלה לוקלית
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
