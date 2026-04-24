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
            return api_response(message="Unauthorized", code=401, status="error")

        user_id = int(user_id_str)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # =========================
        #  1. SUBJECT SUMMARY (MAIN DRIVER)
        # =========================
        cur.execute("""
            SELECT *
            FROM report.student_subject_summary_vw
            WHERE user_id = %s
        """, (user_id,))
        subjects = cur.fetchall()

        total_subjects = len(subjects)

        # =========================
        #  2. LEVEL DATA
        # =========================
        cur.execute("""
            SELECT *
            FROM report.student_subject_level_vw
            WHERE user_id = %s
        """, (user_id,))
        levels = cur.fetchall()

        # =========================
        #  3. CHAPTER DATA
        # =========================
        cur.execute("""
            SELECT *
            FROM report.student_subject_chapter_vw
            WHERE user_id = %s
        """, (user_id,))
        chapters = cur.fetchall()

        # -------------------------------
        #  BUILD FINAL STRUCTURE
        # -------------------------------
        subject_map = {}

        # =========================
        # SUBJECT BASE
        # =========================
        for sub in subjects:
            sid = sub["subject_id"]

            subject_map[sid] = {
                "subject_id": sid,
                "subject_name": sub.get("subject_name"),
                "accuracy": sub.get("accuracy") or 0,
                "avg_time": sub.get("avg_time") or 0,
                "attempted_q": sub.get("attempted_q") or 0,
                "total_attempts": sub.get("total_attempts") or 0,
                "status": "Not Started" if (sub.get("total_attempts") or 0) == 0 else "Attempted",
                "levels": [],
                "chapters": []
            }

        # =========================
        # LEVELS
        # =========================
        for lvl in levels:
            sid = lvl["subject_id"]

            if sid in subject_map:
                subject_map[sid]["levels"].append({
                    "level": lvl.get("level_code"),       # L1,L2,L3,L4
                    "bucket": lvl.get("level_bucket"),    # Easy,Medium,Hard,Expert
                    "accuracy": lvl.get("accuracy") or 0,
                    "avg_time": lvl.get("avg_time") or 0
                })

        #  SORT LEVELS (UI ORDER FIX)
        level_order = {"L1": 1, "L2": 2, "L3": 3, "L4": 4}

        for sid in subject_map:
            subject_map[sid]["levels"] = sorted(
                subject_map[sid]["levels"],
                key=lambda x: level_order.get(x.get("level"), 99)
            )

        # # =========================
        # # CHAPTERS
        # # =========================
        # for ch in chapters:
        #     sid = ch["subject_id"]

        #     if sid in subject_map:
        #         subject_map[sid]["chapters"].append({
        #             "chapter_id": ch.get("chapter_id"),
        #             "chapter_name": ch.get("chapter_name") or ch.get("chapters_name"),
        #             "accuracy": ch.get("accuracy") or 0,
        #             "avg_time": ch.get("avg_time") or 0
        #         })

        # =========================
        # CHAPTERS (LEVEL-WISE FIX)
        # =========================
        chapter_map = {}

        for ch in chapters:
            sid = ch["subject_id"]
            cid = ch["chapter_id"]

            if sid not in subject_map:
                continue

            key = (sid, cid)

            if key not in chapter_map:
                chapter_map[key] = {
                    "chapter_id": cid,
                    "chapter_name": ch.get("chapters_name"),
                    "levels": []
                }

            chapter_map[key]["levels"].append({
                "level": ch.get("level_code"),
                "bucket": ch.get("level_bucket"),
                "accuracy": ch.get("accuracy") or 0,
                "avg_time": ch.get("avg_time") or 0
            })

        # attach to subject
        for (sid, cid), val in chapter_map.items():
            subject_map[sid]["chapters"].append(val)
        # =========================
        # FINAL OUTPUT
        # =========================
        final_data = list(subject_map.values())

        return api_response(
            message="Student Subject Dashboard Loaded",
            code=200,
            status="success",
            data={
                "total_subjects": total_subjects,
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