from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import io
import os
import time

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ========== העלאת תמונה ==========
@app.route("/upload", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    file = request.files["file"]

    # זיהוי סוג התמונה ע"י Pillow
    file_bytes = file.read()
    try:
        img = Image.open(io.BytesIO(file_bytes))
        file_ext = img.format.lower()  # jpg / png / gif / webp
    except Exception:
        return jsonify({"error": "Invalid image"}), 400

    file.stream.seek(0)

    timestamp = int(time.time())
    filename = f"{timestamp}.{file_ext}"

    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    return jsonify({"id": timestamp, "name": filename, "mimeType": f"image/{file_ext}"})


# ========== קבלת רשימת התמונות ==========
@app.route("/files", methods=["GET"])
def list_files():
    files = []
    for fname in os.listdir(UPLOAD_FOLDER):
        if "." not in fname:
            continue

        timestamp_str = fname.split(".")[0]

        if not timestamp_str.isdigit():
            continue

        path = os.path.join(UPLOAD_FOLDER, fname)

        files.append({
            "id": timestamp_str,
            "name": fname,
            "mimeType": f"image/{fname.split('.')[-1]}",
            "createdTime": timestamp_str
        })

    files_sorted = sorted(files, key=lambda x: int(x["id"]), reverse=True)

    return jsonify(files_sorted)


# ========== הצגת תמונה ==========
@app.route("/files/<file_id>/content", methods=["GET"])
def serve_image(file_id):
    for fname in os.listdir(UPLOAD_FOLDER):
        if fname.startswith(file_id):
            return send_from_directory(UPLOAD_FOLDER, fname)
    return jsonify({"error": "File not found"}), 404


# ========== מחיקת תמונה ==========
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
