from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras


def convert_numeric(data):
    for key, value in data.items():
        try:
            num = float(value)

            # 👉 if integer type
            if num.is_integer():
                data[key] = int(num)
            else:
                data[key] = num

        except (ValueError, TypeError):
            pass

    return data



def student_performance_vw():
    conn = None
    cur = None

    try:
        #  AUTH
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(
                message="Unauthorized",
                code=401,
                status="error"
            )

        user_id = int(user_id_str)

        #  DB CONNECT
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # =========================
        #  1. MAIN PERFORMANCE (ALL KPI IN ONE VIEW)
        # =========================
        cur.execute("""
            SELECT *
            FROM report.student_performance_v1_vw
            WHERE user_id = %s
        """, (user_id,))

        performance = cur.fetchone()

        if not performance:
            return api_response(
                message="No data found",
                code=404,
                status="error"
            )
        performance = convert_numeric(performance)
        # =========================
        #  2. TIME DISTRIBUTION (FORMAT FOR UI)
        # =========================
        time_distribution = [
            {"level": "Easy", "avg_time": float(performance.get("easy_avg_time", 0))},
            {"level": "Medium", "avg_time": float(performance.get("medium_avg_time", 0))},
            {"level": "Hard", "avg_time": float(performance.get("hard_avg_time", 0))},
            {"level": "Expert", "avg_time": float(performance.get("expert_avg_time", 0))}
        ]

        # =========================
        # FINAL RESPONSE
        # =========================
        return api_response(
            message="Student Performance Loaded",
            code=200,
            status="success",
            data={
                "performance": performance,
                "time_distribution": time_distribution
            }
        )

    except Exception as e:
        return api_response(
            message="Error fetching student performance",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()