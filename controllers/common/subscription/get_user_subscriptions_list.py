from flask import request
from config import get_db_connection
import jwt
from utils.api_response import api_response
from utils.token_helper import TokenVerifier

def get_user_subscriptions_list():
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(
                message="Unauthorized",
                code=401,
                status="error",
                error=auth_error
            )

        user_id = int(user_id_str)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            CALL subscription.usp_v2_get_user_subscriptions(
                %s,
                NULL,
                NULL,
                NULL
            )
        """, (user_id,))
        result = cur.fetchone()
        p_status = result["p_status"]
        p_message = result["p_message"]
        p_data = result["p_data"]

        return api_response(
            message=p_message,
            code=200,   # always 200
            status=p_status,
            data=p_data
        )
    except Exception as e:
        print("REAL ERROR:", repr(e))
        return api_response(
            message="Internal Server Error",
            code=500,
            status="error",
            error=str(e)
        )
    finally:
        if conn:
            conn.close()
