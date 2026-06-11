from __future__ import annotations

import argparse
import os
import pathlib
import sys
from datetime import date

from dotenv import load_dotenv

# Ensure project root is on sys.path so `from app import ...` works when running as script
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.email_sender import send_email_with_attachment
from app.utils.zman_compute import compute_weekly_pray_times
from app.utils.zman_image import create_zman_image

load_dotenv(ROOT / ".env")  # load .env from project root if present
# Also try to load the system env file if present (e.g. /etc/flaskapp.env)
SYSTEM_ENV = "/etc/flaskapp.env"
if os.path.exists(SYSTEM_ENV):
    try:
        load_dotenv(SYSTEM_ENV, override=True)
        print(f"Loaded system env file: {SYSTEM_ENV}")
    except Exception as e:
        print(f"Could not load {SYSTEM_ENV}: {e}")
else:
    print(f"System env file not found: {SYSTEM_ENV}")


def project_path(value: str) -> str:
    path = pathlib.Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return str(path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate zmanim image and send by email")
    parser.add_argument(
        "--date", help="FRIDAY date (YYYY-MM-DD) to compute week after", default=None)
    parser.add_argument("--to", help="Recipient email address", default=None)
    args = parser.parse_args()

    friday = date.fromisoformat(args.date) if args.date else date.today()

    print(f"Running send_zman_email for friday={friday.isoformat()}")
    # show loaded env (mask password)
    print("ENV:")
    print("  EMAIL_USER=", os.getenv("EMAIL_USER"))
    print("  EMAIL_TO=", os.getenv("EMAIL_TO"))
    print("  ZMANIM_IMAGE_PATH=", os.getenv("ZMANIM_IMAGE_PATH"))
    print("  ZMANIM_LOGO_PATH=", os.getenv("ZMANIM_LOGO_PATH"))

    res = compute_weekly_pray_times(friday)
    shacharit = res.get("shacharit")
    mincha = res.get("mincha")
    arvit = res.get("arvit")

    output_path = project_path(os.getenv("ZMANIM_IMAGE_PATH", "zmanim_output.jpg"))
    logo_path = project_path(os.getenv("ZMANIM_LOGO_PATH", "rashiLogo.PNG"))

    print(f"Creating image at: {output_path} using logo: {logo_path}")
    img_file = create_zman_image(
        shacharit, mincha, arvit, output_path=output_path, logo_path=logo_path)
    to_addr = args.to or os.getenv("EMAIL_TO") or os.getenv(
        "EMAIL_USER") or "yonile2106@gmail.com"

    subject = f"זמני תפילות - שבוע של {friday.isoformat()}"
    body = f"מצורפת תמונה עם זמני התפילות לשבוע שמתחיל אחרי {friday.isoformat()}\n\nשחרית: {shacharit}\nמנחה: {mincha}\nערבית: {arvit}"

    try:
        print(f"Sending email to: {to_addr} with attachment: {img_file}")
        send_email_with_attachment(subject, body, [to_addr], img_file)
        print(f"Sent {img_file} to {to_addr}")
    except Exception as e:
        import traceback

        print("Failed to send email:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
