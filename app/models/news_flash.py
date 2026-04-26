from app import db
from sqlalchemy.sql import func


class NewsFlash(db.Model):
    __tablename__ = "news_flash"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_hebrew = db.Column(db.String(60), nullable=True)
    date_gregorian = db.Column(db.Date, nullable=False)

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
