from flask import Blueprint, request, jsonify, send_from_directory, current_app
from app.services.image_store import save_image, list_images, find_image, delete_image

bp = Blueprint("images_api", __name__)


@bp.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    try:
        data = save_image(request.files["file"],
                          current_app.config["UPLOAD_FOLDER"])
        return jsonify(data)
    except Exception:
        return jsonify({"error": "Invalid image"}), 400


@bp.route("/files", methods=["GET"])
def files():
    return jsonify(list_images(current_app.config["UPLOAD_FOLDER"]))


@bp.route("/files/<file_id>/content", methods=["GET"])
def serve(file_id):
    fname = find_image(current_app.config["UPLOAD_FOLDER"], file_id)
    if not fname:
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], fname)


@bp.route("/files/<file_id>", methods=["DELETE"])
def delete(file_id):
    if delete_image(current_app.config["UPLOAD_FOLDER"], file_id):
        return ("", 204)
    return jsonify({"error": "Not found"}), 404
