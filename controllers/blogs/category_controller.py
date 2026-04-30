from flask import request
from config import get_db_connection
from utils.api_response import api_response
import psycopg2.extras


def get_categories():
    conn = None
    try:

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_get_categories(NULL,NULL,NULL)")
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


def insert_update_category():

    conn = None
    try:

        body = request.json

        category_id = body.get("id")
        category_name = body.get("category_name")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "CALL blog.usp_v1_insert_update_category(%s,%s,NULL,NULL)",
            (category_id, category_name)
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


def delete_category():

    conn = None
    try:

        body = request.json

        category_id = body.get("id")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "CALL blog.usp_v1_delete_category(%s,NULL,NULL)",
            (category_id,)
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
            
            
def get_category_dropdown():

    conn = None
    try:

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_get_category_dropdown(NULL,NULL,NULL)")
        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            data=result["p_object"],
            status="success" if result["p_status_code"] == 200 else "error"
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