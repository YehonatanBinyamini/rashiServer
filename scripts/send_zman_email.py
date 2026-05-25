from __future__ import annotations
from datetime import date
import argparse
from app.utils.zman_compute import compute_weekly_pray_times
from app.utils.zman_image import create_zman_image
from app.services.email_sender import send_email_with_attachment
import os
from dotenv import load_dotenv
import sys
import pathlib

# Ensure project root is on sys.path so `from app import ...` works when running as script
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv()  # load .env from project root if present


def main():
    parser = argparse.ArgumentParser(
        description="Generate zmanim image and send by email")
    parser.add_argument(
        "--date", help="FRIDAY date (YYYY-MM-DD) to compute week after", default=None)
    parser.add_argument("--to", help="Recipient email address", default=None)
    args = parser.parse_args()

    friday = date.fromisoformat(args.date) if args.date else date.today()

    res = compute_weekly_pray_times(friday)
    shacharit = res.get("shacharit")
    mincha = res.get("mincha")
    arvit = res.get("arvit")

    output_path = os.getenv("ZMANIM_IMAGE_PATH", "zmanim_output.jpg")
    logo_path = os.getenv("ZMANIM_LOGO_PATH", "rashiLogo.PNG")

    img_file = create_zman_image(
        shacharit, mincha, arvit, output_path=output_path, logo_path=logo_path)
    to_addr = args.to or os.getenv("EMAIL_TO") or os.getenv(
        "EMAIL_USER") or "yonile2106@gmail.com"

    subject = f"זמני תפילות - שבוע של {friday.isoformat()}"
    body = f"מצורפת תמונה עם זמני התפילות לשבוע שמתחיל אחרי {friday.isoformat()}\n\nשחרית: {shacharit}\nמנחה: {mincha}\nערבית: {arvit}"

    send_email_with_attachment(subject, body, [to_addr], img_file)
    print(f"Sent {img_file} to {to_addr}")


if __name__ == "__main__":
    main()
