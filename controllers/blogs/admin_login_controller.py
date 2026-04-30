from flask import request
from config import get_db_connection
from utils.api_response import api_response
import psycopg2.extras


def admin_login():
    conn = None
    try:

        body = request.json

        username = body.get("username")
        password = body.get("password")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_admin_login(%s,%s,NULL,NULL,NULL)", (username, password))

        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            data=result["p_object"],
            status="success" if result["p_status_code"] == 200 else "error"
        )

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))

    finally:
        if conn:
            cur.close()
            conn.close()