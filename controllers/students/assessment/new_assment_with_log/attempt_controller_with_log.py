from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription # <--- Imported Helper
import psycopg2.extras
import json
 

# 1. Get Assessment Details (Questions)
def get_assessment_details():
    try:
        student_id, error = TokenVerifier.get_user_id()
        if error: return api_response(message=error, code=401)

        assignment_id = request.args.get('assignment_id')
        if not assignment_id:
            return api_response(message="Assignment ID required", code=400)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cur.execute("CALL learning.usp_v1_get_assessment_details(%s, %s, 0, '', '{}')", (assignment_id, student_id))
            res = cur.fetchone()
            return api_response(message=res['o_message'], data=res['o_data'], code=res['o_status'])
        finally:
            cur.close(); conn.close()
    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500)

# 2. finish_assessment  
 

def finish_assessment_with_log():
 
    try:
        # 1. Verify User & Get Data from JWT
        payload = TokenVerifier.get_user_payload()
        if not payload:
            return api_response(message="Unauthorized", code=401, status="error")
            
        student_id = int(payload.get('sub'))
        
        # Extract the specific student's subscription ID directly from their active token!
        student_subscription_id = payload.get('sub_id') 

        # 2. Extract Data from Request
        data = request.get_json()
        attempt_id = data.get('attempt_id')

        if not attempt_id:
            return api_response(message="Attempt ID is required.", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 3. Call Stored Procedure (Now passing student_subscription_id)
            cur.execute(
                """
                CALL learning.usp_v2_finish_assessment_with_log(
                    %s, %s, %s, 0, '', '{}'::JSONB
                )
                """,
                (attempt_id, student_id, student_subscription_id)
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