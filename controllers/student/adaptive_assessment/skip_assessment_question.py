from flask import request
import jwt
import psycopg2.extras
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier



def skip_assessment_question():
    conn = None
    try:
        user_id_str, _ = TokenVerifier.get_user_id()
        logged_in_user_id = int(user_id_str)
        
        json_data = request.get_json()
        attempt_id = json_data.get('attempt_id')
        question_id = json_data.get('question_id')
        time_taken = json_data.get('time_taken', 0)
        sl_no = json_data.get('sl_no') # Extracting sl_no from payload

        sub_token = request.headers.get('Subscription-Id') or request.headers.get('subscription_token')
        sub_payload = jwt.decode(sub_token, options={"verify_signature": False})
        subscription_id = sub_payload.get('sub_id') or sub_payload.get('subscription_id')

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # CALL with 6 parameters + 2 INOUT placeholders
        cur.execute(
            "CALL learning.usp_skip_assessment_question(%s, %s, %s, %s, %s, %s, NULL, NULL)",
            (subscription_id, logged_in_user_id, attempt_id, question_id, time_taken, sl_no)
        )
        
        result = cur.fetchone()
        conn.commit()

        return api_response(
            message=result['o_message'],
            code=result['o_status'],
            status="success" if result['o_status'] == 200 else "error"
        )
    except Exception as e:
        if conn: conn.rollback()
        return api_response(message="Internal Error", error=str(e), code=500, status="error")
    finally:
        if conn: conn.close()