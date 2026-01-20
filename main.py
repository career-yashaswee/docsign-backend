from flask import Flask, jsonify
from flask_cors import CORS
from app.core.config import settings
from app.core.logging import configure_logging


def create_app():
    configure_logging()
    app = Flask(__name__)
    CORS(app)

    @app.get("/health/live")
    def live():
        return jsonify({"status": "live"}), 200

    @app.get("/health/ready")
    def ready():
        # In later stages, check DB, Redis, Celery
        return jsonify({"status": "ready"}), 200

    return app


app = create_app()
