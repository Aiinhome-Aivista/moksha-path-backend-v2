from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras


def teacher_full_dashboard():
    conn = None
    cur = None

    try:
        #  AUTH
        teacher_id_str, _ = TokenVerifier.get_user_id()
        if not teacher_id_str:
            return api_response(message="Unauthorized", code=401, status="error")

        teacher_id = int(teacher_id_str)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # =========================
        #  1. OVERVIEW + SYLLABUS (teacher_dashboard_final)
        # =========================
        cur.execute(
            """
            SELECT response
            FROM report.teacher_dashboard_clean_vw_v1
            WHERE teacher_id = %s
        """,
            (teacher_id,),
        )
        dashboard_main = cur.fetchone()

        # =========================
        #  2. MOCK EXAM
        # =========================
        cur.execute(
            """
            SELECT response
            FROM report.teacher_mock_exam_vw
            WHERE teacher_id = %s
        """,
            (teacher_id,),
        )
        mock_data = cur.fetchone()

        # =========================
        #  3. REMEDIATION
        # =========================
        cur.execute(
            """
            SELECT response
            FROM report.teacher_remediation_vw
            WHERE teacher_id = %s
        """,
            (teacher_id,),
        )
        remediation_data = cur.fetchone()

        # =========================
        #  FINAL RESPONSE BUILD
        # =========================

        final_response = {
            "overview_dashboard": dashboard_main["response"] if dashboard_main else {},
            "mock_exam_dashboard": mock_data["response"] if mock_data else {},
            "remediation_dashboard": (
                remediation_data["response"] if remediation_data else {}
            ),
        }

        return api_response(
            message="Teacher Full Dashboard Loaded",
            code=200,
            status="success",
            data=final_response,
        )

    except Exception as e:
        return api_response(
            message="Error fetching teacher dashboard",
            code=500,
            status="error",
            error=str(e),
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
