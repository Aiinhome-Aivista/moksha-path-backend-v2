from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras


def student_performance_vw():
    conn = None
    cur = None

    try:
        # 🔐 USER AUTH
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error")

        user_id = int(user_id_str)

        # 🛢 DB CONNECT
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # =========================
        # 🔥 1. PERFORMANCE DATA
        # =========================
        cur.execute("""
            SELECT *
            FROM report.student_performance_vw
            WHERE user_id = %s
            ORDER BY attempt_id ASC
        """, (user_id,))
        performance = cur.fetchall()

        # =========================
        # 🔥 2. TOP SUMMARY
        # =========================
        cur.execute("""
            SELECT *
            FROM report.student_dashboard_summary_vw
            WHERE user_id = %s
        """, (user_id,))
        summary = cur.fetchone() or {}

        # =========================
        # 🔥 3. TIME DISTRIBUTION
        # =========================
        cur.execute("""
            SELECT *
            FROM report.student_time_distribution_vw
            WHERE user_id = %s
        """, (user_id,))
        time_dist_rows = cur.fetchall()

        time_distribution = [
            {
                "level": row["difficulty_level"],
                "avg_time": float(row["avg_time"])
            }
            for row in time_dist_rows
        ]

        # =========================
        # 🔥 4. MODULE TEST COUNT
        # =========================
        cur.execute("""
            SELECT 
                COUNT(*) AS total_module_tests,
                COUNT(*) FILTER (WHERE LOWER(status) = 'completed') AS completed_module_tests
            FROM learning.student_assessments_assigned
            WHERE student_id = %s
        """, (user_id,))

        module_stats = cur.fetchone() or {}

        # =========================
        # 🔥 MERGE INTO SUMMARY
        # =========================
        summary["total_module_tests"] = module_stats.get("total_module_tests", 0)
        summary["completed_module_tests"] = module_stats.get("completed_module_tests", 0)

        # =========================
        # 🔥 FINAL RESPONSE
        # =========================
        return api_response(
            message="Student Dashboard Loaded",
            code=200,
            status="success",
            data={
                "top_stats": summary,
                "time_distribution": time_distribution,
                "performance": performance
            }
        )

    except Exception as e:
        return api_response(
            message="Error fetching student dashboard",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()