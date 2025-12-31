import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.config import Config, BASE_DIR

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
    app.config.from_object(Config)

    db.init_app(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    CORS(app, resources={
        r"/*": {
            "origins": app.config["CORS_ORIGINS"],
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "x-api-key"],
            "supports_credentials": True
        }
    })

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.images_api import bp as images_bp
    from app.blueprints.upload_ui import bp as upload_ui_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(images_bp)
    app.register_blueprint(upload_ui_bp)

    @app.route("/")
    def home():
        return "Flask server is running (factory mode)"

    return app
