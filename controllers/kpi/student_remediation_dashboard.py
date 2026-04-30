from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras
from controllers.kpi.student_performance_vw import convert_numeric

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
        # PERFORMANCE
        # =========================
        cur.execute("""
            SELECT *
            FROM report.student_performance_v1_vw
            WHERE user_id = %s
        """, (user_id,))
        performance = cur.fetchone() or {}
        performance = convert_numeric(performance)

        # =========================
        # SUBJECTS
        # =========================
        cur.execute("""
            SELECT *
            FROM report.student_subject_dashboard_v1_vw
            WHERE user_id = %s
        """, (user_id,))
        subjects_raw = cur.fetchall()

        subjects = [
            {
                "subject_id": s.get("subject_id"),
                "subject_name": s.get("subject_name"),
                "chapters": s.get("chapters") or []
            }
            for s in subjects_raw
        ]

        # =========================
        # MOCKS
        # =========================
        cur.execute("""
            SELECT *
            FROM report.student_mock_dashboard_v1_vw
            WHERE user_id = %s
            ORDER BY attempt_id ASC
        """, (user_id,))
        mocks_raw = cur.fetchall()

        level_order = ["L1", "L2", "L3", "L4"]

        def normalize(levels):
            mp = {l["level"]: l for l in (levels or [])}
            return [
                mp.get(lvl, {
                    "level": lvl,
                    "attempted": 0,
                    "correct": 0,
                    "wrong": 0,
                    "skipped": 0,
                    "accuracy": 0,
                    "avg_time": 0
                })
                for lvl in level_order
            ]

        mocks = []
        for row in mocks_raw:
            mocks.append({
                "attempt_id": row.get("attempt_id"),
                "mock_name": row.get("mock_name"),
                "attempt_date": row.get("attempt_date"),
                "overall_score": float(row.get("overall_score") or 0),
                "accuracy_rate": float(row.get("accuracy_rate") or 0),
                "avg_time_per_question": float(row.get("avg_time_per_question") or 0),
                "level_matrix": normalize(row.get("difficulty_matrix")),
                "chapters": row.get("chapter_progression") or []
            })

        # =========================
        # FINAL RESPONSE
        # =========================
        return api_response(
            message="Full Dashboard Loaded",
            code=200,
            status="success",
            data={
                "performance": performance,
                "subjects": {
                    "total_subjects": len(subjects),
                    "list": subjects
                },
                "mocks": {
                    "total_mocks": len(mocks),
                    "list": mocks
                }
            }
        )

    except Exception as e:
        return api_response(
            message="Error fetching dashboard",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()