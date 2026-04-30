from flask import request
from config import get_db_connection
from utils.api_response import api_response
import psycopg2.extras


def get_seo_settings():

    conn = None
    try:

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_get_seo_settings(NULL,NULL,NULL)")
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


def insert_update_seo():

    conn = None
    try:

        body = request.json

        seo_id = body.get("id")
        route = body.get("page_route")
        title = body.get("seo_title")
        description = body.get("seo_description")
        keywords = body.get("seo_keywords")
        canonical = body.get("canonical_url")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "CALL blog.usp_v1_insert_update_seo_settings(%s,%s,%s,%s,%s,%s,NULL,NULL)",
            (seo_id, route, title, description, keywords, canonical)
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
            
            
def delete_seo():

    conn = None
    try:

        body = request.json

        seo_id = body.get("id")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            "CALL blog.usp_v1_delete_seo_settings(%s,NULL,NULL)",
            (seo_id,)
        )

        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
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