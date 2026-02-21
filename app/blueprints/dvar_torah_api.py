from datetime import date, datetime
from convertdate import hebrew
from flask import Blueprint, jsonify, request

from app import db
from app.models.dvar_torah import DvarTorah  # עדכן נתיב אם שונה

bp = Blueprint("dvar_torah_api", __name__, url_prefix="/api/torah")


# מיפוי קבוע: רב -> id (כמו שביקשת)
RABBI_TO_ID = {
    'הרב אברהם יוסף שליט"א': 1,
    "הרב יהונתן בנימיני": 2,
}

HEB_MONTHS = {
    1: "ניסן",
    2: "אייר",
    3: "סיון",
    4: "תמוז",
    5: "אב",
    6: "אלול",
    7: "תשרי",
    8: "חשון",
    9: "כסלו",
    10: "טבת",
    11: "שבט",
    12: "אדר",
    13: "אדר ב׳",
}

HEB_YEARS = {
    5785: 'תשפ״ה',
    5786: 'תשפ״ו',
    5787: 'תשפ״ז',
    5788: 'תשפ״ח',
    5789: 'תשפ״ט',
    5790: 'תש״ץ',
    5791: 'תשצ"א',
    5791: 'תשצ"ב',
    5791: 'תשצ"ג',
    5791: 'תשצ"ד',
    5791: 'תשצ"ה',
    5791: 'תשצ"ו',
}


def to_hebrew_date_str(dt: datetime) -> str:
    """
    מקבל datetime (UTC) ומחזיר מחרוזת עברית כמו: 'כב תמוז תשפה'
    """
    g = dt.date()
    hy, hm, hd = hebrew.from_gregorian(g.year, g.month, g.day)

    month_name = HEB_MONTHS.get(hm, str(hm))
    year_str = HEB_YEARS.get(hy, str(hy))  # fallback אם לא במפה

    # יום בחודש (מספר) -> נשאיר מספר? אצלך זה "כב" (אותיות)
    # אז נמיר לאותיות עבריות בסיסי (1..30)
    day_str = hebrew_day_to_hebrew_letters(hd)

    return f"{day_str} {month_name} {year_str}"


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


HEB_NUM = {
    1: "א", 2: "ב", 3: "ג", 4: "ד", 5: "ה", 6: "ו", 7: "ז", 8: "ח", 9: "ט",
    10: "י", 11: "יא", 12: "יב", 13: "יג", 14: "יד", 15: "טו", 16: "טז",
    17: "יז", 18: "יח", 19: "יט", 20: "כ", 21: "כא", 22: "כב", 23: "כג",
    24: "כד", 25: "כה", 26: "כו", 27: "כז", 28: "כח", 29: "כט", 30: "ל",
}


def hebrew_day_to_hebrew_letters(d: int) -> str:
    return HEB_NUM.get(d, str(d))


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
