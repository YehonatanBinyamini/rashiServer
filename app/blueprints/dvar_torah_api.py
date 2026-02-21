import os
from datetime import datetime, date
from flask import Blueprint, request, jsonify
import psycopg2
import psycopg2.extras

dvar_torah_api = Blueprint("dvar_torah_api", __name__)

# מיפוי קבוע: רב -> id
RABBI_TO_ID = {
    'הרב אברהם יוסף שליט"א': 1,
    "הרב יהונתן בנימיני": 2,
}

# ====== DB connection ======


def get_conn():
    """
    מתאים ל-PostgreSQL.
    אם אצלך יש כבר פונקציה קיימת להתחברות (db.py / engine וכו') – תחליף כאן.
    """
    host = os.getenv("PGHOST", "127.0.0.1")
    port = int(os.getenv("PGPORT", "5432"))
    dbname = os.getenv("PGDATABASE", "flaskappdb")
    user = os.getenv("PGUSER", "flaskuser")
    password = os.getenv("PGPASSWORD", "")

    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )


def row_to_dict(row):
    if not row:
        return None
    out = dict(row)
    dg = out.get("date_gregorian")
    if isinstance(dg, (date, datetime)):
        out["date_gregorian"] = dg.isoformat()
    ca = out.get("created_at")
    if isinstance(ca, datetime):
        out["created_at"] = ca.isoformat()
    return out

# ====== Auth check ======


def is_admin_request(req: request) -> bool:
    """
    מינימלי: אם הגדרת env בשם TORAH_ADMIN_TOKEN,
    חייבים לשלוח Authorization: Bearer <token>.
    אם אין token ב-env -> לא חוסם (נוח לפיתוח).

    אם יש לך כבר auth blueprint עם בדיקה מסודרת,
    אפשר להחליף את הפונקציה הזו לקריאה אליו.
    """
    admin_token = os.getenv("TORAH_ADMIN_TOKEN")
    if not admin_token:
        return True

    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth.split(" ", 1)[1].strip()
    return token == admin_token


@dvar_torah_api.get("/api/torah/latest")
def get_latest_torah():
    rabbi_name = (request.args.get("rabbi_name") or "").strip()
    if rabbi_name not in RABBI_TO_ID:
        return jsonify({"error": "Unknown rabbi_name"}), 400

    torah_id = RABBI_TO_ID[rabbi_name]

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, rabbi_name, title, content, date_hebrew, date_gregorian, created_at
                FROM dvar_torah
                WHERE id = %s
                LIMIT 1
                """,
                (torah_id,),
            )
            row = cur.fetchone()

    if not row:
        return jsonify({"error": "Row not found"}), 404

    return jsonify(row_to_dict(row))


@dvar_torah_api.post("/api/torah/save")
def save_torah():
    if not is_admin_request(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}

    rabbi_name = (data.get("rabbi_name") or "").strip()
    if rabbi_name not in RABBI_TO_ID:
        return jsonify({"error": "Unknown rabbi_name"}), 400

    torah_id = RABBI_TO_ID[rabbi_name]

    # השדות שמותר לעדכן (לא id ולא rabbi_name)
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    date_hebrew = (data.get("date_hebrew") or "").strip() or None

    # NOT NULL אצלך - אם לא שולחים, נשים היום
    date_gregorian_raw = data.get("date_gregorian")
    if isinstance(date_gregorian_raw, str) and date_gregorian_raw.strip():
        dg_str = date_gregorian_raw.strip()
        try:
            date_gregorian = datetime.fromisoformat(
                dg_str).date()  # תומך גם ISO
        except ValueError:
            try:
                date_gregorian = datetime.strptime(dg_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid date_gregorian format"}), 400
    else:
        date_gregorian = date.today()

    created_at = datetime.utcnow()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE dvar_torah
                SET title = %s,
                    content = %s,
                    date_hebrew = %s,
                    date_gregorian = %s,
                    created_at = %s
                WHERE id = %s
                """,
                (title, content, date_hebrew, date_gregorian, created_at, torah_id),
            )

            if cur.rowcount != 1:
                return jsonify({"error": "Update failed (row not found)"}), 404

        conn.commit()

    # נחזיר את הרשומה המעודכנת
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, rabbi_name, title, content, date_hebrew, date_gregorian, created_at
                FROM dvar_torah
                WHERE id = %s
                LIMIT 1
                """,
                (torah_id,),
            )
            row = cur.fetchone()

    return jsonify(row_to_dict(row))
