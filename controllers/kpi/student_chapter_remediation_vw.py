from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras


def student_chapter_remediation_vw():
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
            FROM report.vw_student_chapter_remediation
            WHERE user_id = %s
            ORDER BY overall_accuracy ASC   -- weakest first
        """, (user_id,))

        rows = cur.fetchall()

        if not rows:
            return api_response(
                message="No remediation data",
                code=200,
                status="success",
                data=[]
            )

        # ✅ CLEAN RESPONSE FORMAT
        result = []
        for r in rows:
            result.append({
                "chapter_id": r["chapter_id"],
                "chapter_name": r["chapters_name"],
                "subject_id": r["subject_id"],

                # performance
                "overall_accuracy": float(r["overall_accuracy"] or 0),

                # level accuracy
                "levels": {
                    "L1": float(r["l1_accuracy"] or 0),
                    "L2": float(r["l2_accuracy"] or 0),
                    "L3": float(r["l3_accuracy"] or 0),
                    "L4": float(r["l4_accuracy"] or 0),
                },

                # counts
                "attempted": r["attempted"],
                "correct": r["correct"],
                "wrong": r["wrong"],
                "skipped": r["skipped"],

                # insights
                "priority": r["priority_status"],
                "current_level": r["current_level"],

                # recommendations
                "recommendations": [
                    r["recommendation_1"],
                    r["recommendation_2"],
                    r["recommendation_3"]
                ]
            })

        return api_response(
            message="Chapter Remediation Loaded",
            code=200,
            status="success",
            data=result
        )

    except Exception as e:
        return api_response(
            message="Error fetching remediation",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()