from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras


def student_subject_dashboard_vw():
    conn = None
    cur = None

    try:
        #  USER
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(
                message="Unauthorized",
                code=401,
                status="error"
            )

        user_id = int(user_id_str)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # =========================
        #  SINGLE QUERY (NEW VIEW)
        # =========================
        cur.execute("""
            SELECT *
            FROM report.student_subject_dashboard_v1_vw
            WHERE user_id = %s
        """, (user_id,))

        subjects = cur.fetchall()

        # =========================
        # FORMAT RESPONSE
        # =========================
        final_data = []

        for sub in subjects:
            final_data.append({
                "subject_id": sub.get("subject_id"),
                "subject_name": sub.get("subject_name"),
                "chapters": sub.get("chapters") or []
            })

        return api_response(
            message="Student Subject Dashboard Loaded",
            code=200,
            status="success",
            data={
                "total_subjects": len(final_data),
                "subjects": final_data
            }
        )

    except Exception as e:
        return api_response(
            message="Error fetching subject dashboard",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()