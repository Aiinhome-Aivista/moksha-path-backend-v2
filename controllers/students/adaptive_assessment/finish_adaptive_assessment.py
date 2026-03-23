from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras
import json
import jwt 

def finish_adaptive_assessment():
    try:
        # 1. Auth & Payload
        payload = TokenVerifier.get_user_payload()
        if not payload:
            return api_response(message="Unauthorized", code=401, status="error")
            
        student_id = int(payload.get('sub'))
        student_subscription_id = payload.get('sub_id') 

        data = request.get_json()
        attempt_id = data.get('attempt_id')

        if not attempt_id:
            return api_response(message="Attempt ID is required.", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 2. Call Procedure
            cur.execute(
                "CALL learning.usp_v2_finish_assessment_with_log(%s, %s, %s, NULL, NULL, NULL)",
                (int(attempt_id), student_id, student_subscription_id)
            )
            result = cur.fetchone()
            conn.commit()

            if result['o_status'] == 200:
                return api_response(message=result['o_message'], data=result['o_data'], code=200, status="success")
            else:
                return api_response(message=result['o_message'], code=result['o_status'], status="error")

        except Exception as db_err:
            conn.rollback()
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")