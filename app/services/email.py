import random
import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


async def send_otp_email(email: str, otp: str) -> None:
    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = email
    message["Subject"] = "QRTifact — Your verification code"
    message.set_content(f"""
Your verification code is:

{otp}

This code expires in 10 minutes.
""")

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
