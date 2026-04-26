from datetime import date, datetime
from flask import Blueprint, jsonify, request

from app import db
from app.models.news_flash import NewsFlash


bp = Blueprint("news_flash_api", __name__, url_prefix="/api/news")


def _as_dict(row: NewsFlash):
    return {
        "id": row.id,
        "title": row.title,
        "content": row.content,
        "date_hebrew": row.date_hebrew,
        "date_gregorian": row.date_gregorian.isoformat() if row.date_gregorian else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


def _parse_date_gregorian(val):
    if not val:
        return date.today()

    if isinstance(val, str):
        s = val.strip()
        if not s:
            return date.today()
        # try ISO
        try:
            return datetime.fromisoformat(s).date()
        except ValueError:
            pass
        # try YYYY-MM-DD
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date_gregorian format")

    raise ValueError("Invalid date_gregorian type")


@bp.get("/")
def list_news():
    """
    List all news flashes (most recent first). Optional query `limit`.
    """
    try:
        limit = int(request.args.get("limit") or 0)
    except ValueError:
        return jsonify({"error": "invalid limit"}), 400

    q = db.session.query(NewsFlash).order_by(NewsFlash.date_gregorian.desc(), NewsFlash.id.desc())
    if limit > 0:
        q = q.limit(limit)

    rows = q.all()
    return jsonify([_as_dict(r) for r in rows])


@bp.get("/<int:row_id>")
def get_news(row_id: int):
    row = db.session.get(NewsFlash, row_id)
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(_as_dict(row))


@bp.post("/")
def create_news():
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    date_hebrew = (data.get("date_hebrew") or "").strip() or None

    if not title:
        return jsonify({"error": "title is required"}), 400
    if not content:
        return jsonify({"error": "content is required"}), 400

    try:
        date_gregorian = _parse_date_gregorian(data.get("date_gregorian"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    row = NewsFlash(
        title=title,
        content=content,
        date_hebrew=date_hebrew,
        date_gregorian=date_gregorian,
    )

    db.session.add(row)
    db.session.commit()

    return jsonify(_as_dict(row)), 201


@bp.put("/<int:row_id>")
def update_news(row_id: int):
    data = request.get_json(silent=True) or {}

    row = db.session.get(NewsFlash, row_id)
    if not row:
        return jsonify({"error": "not found"}), 404

    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    date_hebrew = (data.get("date_hebrew") or "").strip() or None

    if title:
        row.title = title
    if content:
        row.content = content

    try:
        if "date_gregorian" in data:
            row.date_gregorian = _parse_date_gregorian(data.get("date_gregorian"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    row.date_hebrew = date_hebrew

    db.session.commit()

    return jsonify(_as_dict(row))


@bp.delete("/<int:row_id>")
def delete_news(row_id: int):
    row = db.session.get(NewsFlash, row_id)
    if not row:
        return jsonify({"error": "not found"}), 404

    db.session.delete(row)
    db.session.commit()

    return jsonify({"ok": True})
