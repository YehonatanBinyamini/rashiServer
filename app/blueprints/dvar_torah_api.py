from datetime import date, datetime
from flask import Blueprint, jsonify, request

from app import db
from app.models.dvar_torah import DvarTorah  # עדכן נתיב אם שונה
from app.utils.hebrew_date import to_hebrew_date_str

bp = Blueprint("dvar_torah_api", __name__, url_prefix="/api/torah")


# מיפוי קבוע: רב -> id (כמו שביקשת)
RABBI_TO_ID = {
    'הרב אברהם יוסף שליט"א': 1,
    "הרב יהונתן בנימיני": 2,
}


def _parse_date_gregorian(val):
    """
    קולט:
    - None / "" -> היום
    - "YYYY-MM-DD"
    - ISO (כולל זמן) -> לוקח date()
    """
    if not val:
        return date.today()

    if isinstance(val, str):
        s = val.strip()
        if not s:
            return date.today()
        # ISO
        try:
            return datetime.fromisoformat(s).date()
        except ValueError:
            pass
        # YYYY-MM-DD
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date_gregorian format")

    raise ValueError("Invalid date_gregorian type")


def _as_dict(row: DvarTorah):
    return {
        "id": row.id,
        "rabbi_name": row.rabbi_name,
        "title": row.title,
        "content": row.content,
        "date_hebrew": row.date_hebrew,
        "date_gregorian": row.date_gregorian.isoformat() if row.date_gregorian else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


@bp.get("/latest")
def get_latest():
    """
    מחזיר את הרשומה הקבועה לפי rabbi_name (מיפוי ל-id 1/2).
    """
    rabbi_name = (request.args.get("rabbi_name") or "").strip()
    if rabbi_name not in RABBI_TO_ID:
        return jsonify({"error": "Unknown rabbi_name"}), 400

    torah_id = RABBI_TO_ID[rabbi_name]

    row = db.session.get(DvarTorah, torah_id)
    if not row:
        return jsonify({"error": "Row not found (id missing)"}), 404

    return jsonify(_as_dict(row))


@bp.post("/save")
def save():
    """
    UPDATE בלבד לרשומה הקבועה.
    מעדכן את כל השדות חוץ מ-id ו-rabbi_name:
    title, content, date_hebrew, date_gregorian, created_at
    """
    data = request.get_json(silent=True) or {}

    rabbi_name = (data.get("rabbi_name") or "").strip()
    if rabbi_name not in RABBI_TO_ID:
        return jsonify({"error": "Unknown rabbi_name"}), 400

    torah_id = RABBI_TO_ID[rabbi_name]

    row = db.session.get(DvarTorah, torah_id)
    if not row:
        return jsonify({"error": "Row not found (id missing)"}), 404

    # לא נוגעים ב: row.id, row.rabbi_name
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    date_hebrew = (data.get("date_hebrew") or "").strip() or None

    try:
        date_gregorian = _parse_date_gregorian(data.get("date_gregorian"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    row.title = title
    row.content = content
    row.date_gregorian = date_gregorian
    row.date_hebrew = to_hebrew_date_str(row.updated_at)

    db.session.commit()

    return jsonify(_as_dict(row))
