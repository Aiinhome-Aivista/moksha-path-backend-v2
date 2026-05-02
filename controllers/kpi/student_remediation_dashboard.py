from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras
import json


def student_remediation_dashboard():
    conn = None
    cur = None

    try:
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error")

        user_id = int(user_id_str)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # =========================
        # ONLY NEW VIEW CALL
        # =========================
        cur.execute("""
            SELECT final_json
            FROM report.student_remediation_vw
            WHERE user_id = %s
        """, (user_id,))

        row = cur.fetchone()

        if not row:
            return api_response(
                message="No data found",
                code=404,
                status="error"
            )

        # JSON parse (important)
        data = row.get("final_json")

        if isinstance(data, str):
            data = json.loads(data)

        # =========================
        # FINAL RESPONSE
        # =========================
        return api_response(
            message="Student Remediation Dashboard Loaded",
            code=200,
            status="success",
            data=data
        )

    except Exception as e:
        return api_response(
            message="Error fetching remediation dashboard",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()