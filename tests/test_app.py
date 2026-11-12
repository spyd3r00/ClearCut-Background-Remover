from io import BytesIO
import os
import sys
from tempfile import gettempdir
from types import ModuleType

from PIL import Image

from app import create_app


def test_home_page():
    response = create_app().test_client().get("/")

    assert response.status_code == 200
    assert b"Background Remover" in response.data
    assert b"Remove background" in response.data
    assert b"<select" not in response.data
    assert b'name="model"' not in response.data
    assert b"up to 4 MB" in response.data


def test_upload_limit_is_4_mb():
    app = create_app()

    assert app.config["MAX_CONTENT_LENGTH"] == 4 * 1024 * 1024 + 64 * 1024


def test_remove_background_returns_png(monkeypatch):
    monkeypatch.delenv("U2NET_HOME", raising=False)
    output = BytesIO()
    Image.new("RGBA", (1, 1), (255, 0, 0, 0)).save(output, format="PNG")
    expected_png = output.getvalue()
    rembg = ModuleType("rembg")

    def new_session(model):
        assert os.environ["U2NET_HOME"] == os.path.join(gettempdir(), "rembg")
        return model

    rembg.new_session = new_session
    rembg.remove = lambda image, session, **options: (
        expected_png
        if image
        and session == "isnet-general-use"
        and options.get("decontaminate") is True
        else b""
    )
    monkeypatch.setitem(sys.modules, "rembg", rembg)

    image = BytesIO()
    Image.new("RGB", (1, 1), (255, 0, 0)).save(image, format="PNG")
    response = create_app().test_client().post(
        "/remove",
        data={"image": (BytesIO(image.getvalue()), "photo.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.data == expected_png


def test_remove_background_rejects_unknown_model():
    response = create_app().test_client().post(
        "/remove",
        data={"image": (BytesIO(b"not an image"), "photo.png"), "model": "unknown"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.json == {"error": "Choose a supported image type."}


def test_remove_background_rejects_non_image():
    response = create_app().test_client().post(
        "/remove",
        data={"image": (BytesIO(b"not an image"), "photo.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.json == {"error": "That file is not a valid image."}


def test_remove_background_requires_a_file():
    response = create_app().test_client().post("/remove")

    assert response.status_code == 400
    assert response.json == {"error": "Choose an image to continue."}


def test_remove_background_rejects_large_dimensions():
    app = create_app()
    app.config["MAX_IMAGE_PIXELS"] = 0
    image = BytesIO()
    Image.new("RGB", (1, 1), (255, 0, 0)).save(image, format="PNG")

    response = app.test_client().post(
        "/remove",
        data={"image": (BytesIO(image.getvalue()), "photo.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    assert response.json == {"error": "The image resolution is too large to process."}
