from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Iterable


DEFAULT_SMTP = "smtp.gmail.com"
DEFAULT_PORT = 587


def send_email_with_attachment(subject: str, body: str, to_addrs: Iterable[str], attachment_path: str, smtp_user: str | None = None, smtp_pass: str | None = None) -> None:
    smtp_user = smtp_user or os.getenv("EMAIL_USER") or "yonile2106@gmail.com"
    smtp_pass = smtp_pass or os.getenv("EMAIL_PASS") or "kafw pydx apjr zkaj"
    to_addrs = list(to_addrs)

    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.set_content(body)

    # attach image
    with open(attachment_path, "rb") as f:
        img_data = f.read()
    maintype = "image"
    subtype = "jpeg"
    msg.add_attachment(img_data, maintype=maintype, subtype=subtype,
                       filename=os.path.basename(attachment_path))

    with smtplib.SMTP(DEFAULT_SMTP, DEFAULT_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)
