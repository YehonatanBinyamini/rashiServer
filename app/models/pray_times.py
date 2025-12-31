from datetime import datetime, timezone
from app import db


class PrayTimes(db.Model):
    __tablename__ = "pray_times"

    id = db.Column(db.Integer, primary_key=True)

    date_gregorian = db.Column(
        db.Date, nullable=False, unique=True, index=True)

    shacharit = db.Column(db.String(5), nullable=False)
    mincha = db.Column(db.String(5), nullable=False)
    arvit = db.Column(db.String(5), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
