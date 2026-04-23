from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras


def student_mock_dashboard_vw():
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
            SELECT *
            FROM report.student_mock_dashboard_vw
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        row = cur.fetchone()

        if not row:
            return api_response(message="No data", code=200, status="success", data={})

        # ✅ LEVEL NORMALIZATION (L1–L4 ALWAYS)
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

        mcq = row.get("mcq") or {}
        quiz = row.get("quiz") or {}

        return api_response(
            message="Mock Dashboard Loaded",
            code=200,
            status="success",
            data={
                "mcq": {
                    "level_matrix": normalize(mcq.get("level_matrix")),
                    "chapters": mcq.get("chapters") or []
                },
                "quiz": {
                    "level_matrix": normalize(quiz.get("level_matrix")),
                    "chapters": quiz.get("chapters") or []
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