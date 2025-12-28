from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
from app.services.image_store import save_image

bp = Blueprint("upload_ui", __name__)


@bp.route("/upload-ui", methods=["GET"])
def upload_ui():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))
    return render_template("upload.html")


@bp.route("/upload-direct", methods=["POST"])
def upload_direct():
    if not session.get("logged_in"):
        return "לא מורשה", 401

    if "file" not in request.files:
        return "לא נבחר קובץ", 400

    try:
        data = save_image(request.files["file"],
                          current_app.config["UPLOAD_FOLDER"])
        return f"תמונה הועלתה בהצלחה: {data['name']}"
    except Exception:
        return "קובץ לא תקין", 400
