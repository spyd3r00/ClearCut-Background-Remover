# Clearcut Background Remover

A Flask website that removes image backgrounds with the CPU version of
[rembg](https://github.com/danielgatis/rembg). It accepts PNG, JPG, and WebP
images, then returns a transparent PNG. It uses the Photo / general image
model by default.

## Run locally on Windows

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Open <http://127.0.0.1:5000>. On the first removal for each mode, rembg
downloads its model to your user cache; later runs reuse it.

Uploads are limited to 4 MB and 25 megapixels. The app returns results directly
to the browser and does not save uploaded or processed images.

## Run tests

```powershell
python -m pytest
```
