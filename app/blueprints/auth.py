from flask import Blueprint, request, render_template, redirect, url_for, session, current_app

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd == current_app.config["UPLOAD_PASSWORD"]:
            session["logged_in"] = True
            return redirect(url_for("upload_ui.upload_ui"))
        return render_template("login.html", error="סיסמה שגויה")

    return render_template("login.html", error=None)
