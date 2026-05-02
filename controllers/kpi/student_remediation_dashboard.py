from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
from utils.remediation_helper import get_remediation_pointers
import psycopg2.extras
import json

def student_remediation_dashboard():
    """
    Returns only the student performance data (Original state, no AI).
    """
    conn = None
    cur = None

    try:
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error")

        user_id = int(user_id_str)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

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

        data = row.get("final_json")
        if isinstance(data, str):
            data = json.loads(data)

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

def student_remediation_ai_insights():
    """
    New separate function: Fetches data and returns AI remediation pointers.
    """
    conn = None
    cur = None
    try:
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error")

        user_id = int(user_id_str)
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT final_json
            FROM report.student_remediation_vw
            WHERE user_id = %s
        """, (user_id,))

        row = cur.fetchone()
        if not row:
            return api_response(message="No data found for AI analysis", code=404, status="error")

        student_performance = row.get("final_json")

        # Call AI helper for insights
        ai_remediation = get_remediation_pointers(student_performance)

        return api_response(
            message="AI Remediation Insights Generated",
            code=200,
            status="success",
            data={
                "remediation": ai_remediation
            }
        )

    except Exception as e:
        return api_response(message="Error generating AI insights", code=500, status="error", error=str(e))
    finally:
        if cur: cur.close()
        if conn: conn.close()
