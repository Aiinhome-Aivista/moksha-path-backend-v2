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

        # ============================================
        # 🔥 STEP 1: LATEST MULTI-CHAPTER ATTEMPT
        # ============================================
        cur.execute("""
            SELECT DISTINCT attempt_id
            FROM report.student_mock_chapter_vw
            WHERE user_id = %s
            ORDER BY attempt_id DESC
            LIMIT 1
        """, (user_id,))

        row = cur.fetchone()

        if not row:
            return api_response(message="No data", code=200, status="success", data={})

        attempt_id = row["attempt_id"]

        # ============================================
        # 🔥 STEP 2: TOP (TYPE-WISE)
        # ============================================
        cur.execute("""
            SELECT *
            FROM report.student_mock_top_vw
            WHERE user_id = %s AND attempt_id = %s
        """, (user_id, attempt_id))

        top_rows = cur.fetchall()

        mcq_top = {}
        tf_top = {}

        for t in top_rows:
            obj = {
                "accuracy": float(t.get("accuracy", 0) or 0),
                "avg_time": float(t.get("avg_time", 0) or 0)
            }

            if t.get("question_type") == "MCQ":
                mcq_top = obj
            else:
                tf_top = obj

        # ============================================
        # 🔥 STEP 3: LEVEL MATRIX
        # ============================================
        cur.execute("""
            SELECT *
            FROM report.student_mock_level_matrix_vw
            WHERE user_id = %s AND attempt_id = %s
        """, (user_id, attempt_id))

        levels = cur.fetchall()

        level_order = ["L1", "L2", "L3", "L4"]

        mcq_map = {}
        tf_map = {}

        for l in levels:
            obj = {
                "level": l.get("level"),
                "attempted": l.get("attempted", 0),
                "correct": l.get("correct", 0),
                "wrong": l.get("wrong", 0),
                "skipped": l.get("skipped", 0),
                "accuracy": float(l.get("accuracy", 0) or 0),
                "avg_time": float(l.get("avg_time", 0) or 0)
            }

            if l.get("question_type") == "MCQ":
                mcq_map[l.get("level")] = obj
            else:
                tf_map[l.get("level")] = obj

        mcq_levels = []
        tf_levels = []

        for lvl in level_order:
            mcq_levels.append(mcq_map.get(lvl, {
                "level": lvl,
                "attempted": 0,
                "correct": 0,
                "wrong": 0,
                "skipped": 0,
                "accuracy": 0,
                "avg_time": 0
            }))

            tf_levels.append(tf_map.get(lvl, {
                "level": lvl,
                "attempted": 0,
                "correct": 0,
                "wrong": 0,
                "skipped": 0,
                "accuracy": 0,
                "avg_time": 0
            }))

        # ============================================
        # 🔥 STEP 4: CHAPTER
        # ============================================
        cur.execute("""
            SELECT *
            FROM report.student_mock_chapter_vw
            WHERE user_id = %s AND attempt_id = %s
        """, (user_id, attempt_id))

        chapters = cur.fetchall()

        mcq_chapters = []
        tf_chapters = []

        for c in chapters:
            obj = {
                "chapter_id": c.get("chapter_id"),
                "chapter_name": c.get("chapters_name"),
                "accuracy": float(c.get("accuracy", 0) or 0),
                "label": f"Handles {c.get('strongest_level')}"
            }

            if c.get("question_type") == "MCQ":
                mcq_chapters.append(obj)
            else:
                tf_chapters.append(obj)

        # ============================================
        # 🚀 FINAL RESPONSE
        # ============================================
        return api_response(
            message="Mock Dashboard Loaded",
            code=200,
            status="success",
            data={
                "top_stats": {
                    "mcq": mcq_top,
                    "truefalse": tf_top
                },
                "level_matrix": {
                    "mcq": mcq_levels,
                    "truefalse": tf_levels
                },
                "chapters": {
                    "mcq": mcq_chapters,
                    "truefalse": tf_chapters
                }
            }
        )

    except Exception as e:
        return api_response(
            message="Error fetching mock dashboard",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()