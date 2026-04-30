from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras
import json
import jwt 


def finish_adaptive_assessment():
    conn = None
    try:
        # 1. AUTH
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        # 2. PAYLOAD
        data = request.get_json()
        attempt_id = data.get('attempt_id')
        subscription_id = data.get('subscription_id')

        # 3. DB CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            "CALL learning.usp_v2_finish_addaptive_assessment_with_log(%s, %s, %s, NULL, NULL, NULL)",
            (int(attempt_id), int(user_id_str), subscription_id)
        )

        result = cur.fetchone()
        conn.commit()

        # Handle result using names 'o_status', 'o_message', 'o_data'
        if result and result.get('o_status') == 200:
            return api_response(
                message=result.get('o_message'), 
                data=result.get('o_data'), 
                code=200, 
                status="success"
            )
        else:
            return api_response(
                message=result.get('o_message', 'Submission error'), 
                code=result.get('o_status', 400), 
                status="error"
            )

    except Exception as e:
        if conn: conn.rollback()
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: 
            conn.close()
            cur.close()
