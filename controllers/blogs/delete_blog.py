
from flask import request
from config import get_db_connection
from utils.api_response import api_response

def delete_blog():

    conn = None
    try:

        body = request.json

        blog_id = body.get("id")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "CALL blog.usp_v1_delete_blog(%s,NULL,NULL)",
            (blog_id,)
        )

        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            status="success" if result["p_status_code"] == 200 else "error"
        )

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))

    finally:
        if conn:
            cur.close()
            conn.close()

