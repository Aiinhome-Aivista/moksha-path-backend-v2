from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras


def student_mock_dashboard_vw():
    conn = None
    cur = None

    try:
        #  AUTH
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error")

        user_id = int(user_id_str)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        #  FETCH ALL MOCKS
        cur.execute(
            """
            SELECT *
            FROM report.student_mock_dashboard_v1_vw
            WHERE user_id = %s
            ORDER BY attempt_id ASC
            """,
            (user_id,),
        )

        rows = cur.fetchall()

        if not rows:
            return api_response(
                message="No data", code=200, status="success", data={"mocks": []}
            )

        #  LEVEL NORMALIZATION
        level_order = ["L1", "L2", "L3", "L4"]

        def normalize(levels):
            mp = {l["level"]: l for l in (levels or [])}
            return [
                mp.get(
                    lvl,
                    {
                        "level": lvl,
                        "attempted": 0,
                        "correct": 0,
                        "wrong": 0,
                        "skipped": 0,
                        "accuracy": 0,
                        "avg_time": 0,
                    },
                )
                for lvl in level_order
            ]

        mocks = []

        for row in rows:
            level_matrix = row.get("difficulty_matrix") or []
            chapters = row.get("chapter_progression") or []

            mocks.append(
                {
                    "attempt_id": row.get("attempt_id"),
                    "mock_name": row.get("mock_name"),
                    "attempt_date": row.get("attempt_date"),
                    "overall_score": float(row.get("overall_score") or 0),
                    "accuracy_rate": float(row.get("accuracy_rate") or 0),
                    "avg_time_per_question": float(
                        row.get("avg_time_per_question") or 0
                    ),
                    "level_matrix": normalize(level_matrix),
                    "chapters": chapters,
                }
            )

        return api_response(
            message="Mock Dashboard Loaded",
            code=200,
            status="success",
            data={"mocks": mocks},
        )

    except Exception as e:
        return api_response(
            message="Error fetching dashboard", code=500, status="error", error=str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()