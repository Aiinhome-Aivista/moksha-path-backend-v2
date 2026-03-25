from flask import request
from config import get_db_connection
from utils.api_response import api_response
import psycopg2.extras
import json
def log_activity():
    conn = None
    try:
        data = request.json

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            "CALL analytics.insert_user_activity(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                data.get("user_id"),
                data.get("role"),
                data.get("email"),
                data.get("event_name"),
                data.get("page"),
                data.get("url"),
                data.get("method"),
                data.get("status"),
                json.dumps(data)
            )
        )

        conn.commit()  # ✅ IMPORTANT

        return api_response(
            message="Logged successfully",
            code=200,
            status="success"
        )

    except Exception as e:
        return api_response(
            message="Internal Server Error",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if conn:
            cur.close()
            conn.close()