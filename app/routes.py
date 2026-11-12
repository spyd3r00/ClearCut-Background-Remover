from functools import lru_cache
from io import BytesIO

from flask import Blueprint, current_app, jsonify, render_template, request, send_file
from PIL import Image, UnidentifiedImageError


main = Blueprint("main", __name__)
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}
MODEL_OPTIONS = {
    "anime": "isnet-anime",
    "general": "isnet-general-use",
}


@lru_cache(maxsize=2)
def _get_rembg_session(model_name):
    from rembg import new_session

    return new_session(model_name)


@main.get("/")
def home():
    return render_template("index.html")


@main.post("/remove")
def remove_background():
    upload = request.files.get("image")
    if upload is None or not upload.filename:
        return jsonify(error="Choose an image to continue."), 400

    model_choice = request.form.get("model", "general")
    if model_choice not in MODEL_OPTIONS:
        return jsonify(error="Choose a supported image type."), 400

    image_data = upload.read()
    if not image_data:
        return jsonify(error="The selected file is empty."), 400

    try:
        with Image.open(BytesIO(image_data)) as image:
            image_format = image.format
            width, height = image.size
            image.verify()
    except (Image.DecompressionBombError, OSError, UnidentifiedImageError):
        return jsonify(error="That file is not a valid image."), 400

    if image_format not in ALLOWED_IMAGE_FORMATS:
        return jsonify(error="Use a PNG, JPG, or WebP image."), 400

    if width * height > current_app.config["MAX_IMAGE_PIXELS"]:
        return jsonify(error="The image resolution is too large to process."), 413

    from rembg import remove

    result = remove(
        image_data,
        session=_get_rembg_session(MODEL_OPTIONS[model_choice]),
    )
    return send_file(BytesIO(result), mimetype="image/png")
