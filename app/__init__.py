from flask import Flask, jsonify
from werkzeug.exceptions import RequestEntityTooLarge

from app.routes import main


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=4 * 1024 * 1024 + 64 * 1024,
        MAX_IMAGE_PIXELS=25_000_000,
    )
    app.register_blueprint(main)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_upload(_):
        return jsonify(error="The image is too large. The upload limit is 4 MB."), 413

    return app
