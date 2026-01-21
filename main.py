import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.core.config import settings
from app.core.logging import configure_logging


from app.routes.auth import auth_bp
from app.routes.document import documents_bp


def create_app():
    configure_logging()
    app = Flask(__name__)
    CORS(app)

    if settings.JWT_SECRET_KEY:
        app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
        jwt = JWTManager(app)

        @jwt.invalid_token_loader
        def invalid_token_callback(reason):
            return jsonify({"error": "invalid_token", "detail": reason}), 401

        @jwt.unauthorized_loader
        def missing_token_callback(reason):
            return jsonify({"error": "missing_token", "detail": reason}), 401

        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return jsonify({"error": "token_expired"}), 401

        @jwt.needs_fresh_token_loader
        def needs_fresh_token_callback(jwt_header, jwt_payload):
            return jsonify({"error": "fresh_token_required"}), 401

    # Max payload size (Flask expects bytes)
    app.config["MAX_CONTENT_LENGTH"] = settings.MAX_CONTENT_LENGTH_MB * 1024 * 1024

    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # BluePrints
    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)

    @app.get("/health/live")
    def live():
        return jsonify({"status": "live"}), 200

    @app.get("/health/ready")
    def ready():
        # In later stages, check DB, Redis, Celery
        return jsonify({"status": "ready"}), 200

    return app


app = create_app()
