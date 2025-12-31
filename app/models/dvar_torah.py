from datetime import datetime, timezone
from app import db


class DvarTorah(db.Model):
    __tablename__ = "dvar_torah"

    id = db.Column(db.Integer, primary_key=True)

    rabbi_name = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    date_hebrew = db.Column(db.String(60), nullable=True)
    date_gregorian = db.Column(db.Date, nullable=False, index=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
