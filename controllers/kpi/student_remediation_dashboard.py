from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
from utils.remediation_helper import get_remediation_pointers
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

        # Fetch student performance data
        student_performance = row.get("final_json")
        
        # Parse original data (maintain previous structure)
        if isinstance(student_performance, str):
            data = json.loads(student_performance)
        else:
            data = student_performance

        # =========================
        # AI INSIGHTS GENERATION
        # =========================
        # Using the helper to get insights and adding it to original data
        data["remediation"] = get_remediation_pointers(student_performance)

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
