import io
import uuid
import qrcode
from app.core.config import settings


def generate_qr_png(url: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def save_qr_locally(png_bytes: bytes, filename: str) -> str:
    import os
    path = f"static/uploads/qr/{filename}"
    os.makedirs("static/uploads/qr", exist_ok=True)
    with open(path, "wb") as f:
        f.write(png_bytes)
    return f"{settings.BACKEND_URL}/{path}"
