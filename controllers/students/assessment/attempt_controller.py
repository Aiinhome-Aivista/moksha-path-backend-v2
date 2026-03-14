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

# 2. Start Assessment Attempt

 
def start_assessment_attempt():
    """
    POST /api/v1/assessment/start
    Body: { "assignment_id": 123 }
    """
    try:
        # 1. Get User Payload
        payload = TokenVerifier.get_user_payload()
        if not payload:
            return api_response(message="Unauthorized", code=401)
            
        student_id = payload.get('sub')

        # =========================================================================
        # 2. Extract Default Subscription ID directly from JWT (Bypass old helper)
        # =========================================================================
        subscription_id = None
        roles = payload.get('roles', [])
        
        for role in roles:
            if role.get('is_default') is True:
                subscription_id = role.get('subscription_id')
                break
        
        if not subscription_id:
            subscription_id = payload.get('sub_id') or payload.get('subscription_id')

        if not subscription_id:
             return api_response(message="Active Subscription ID not found for this user.", code=403, status="error")

        # 3. Get Request Data
        data = request.get_json()
        assignment_id = data.get('assignment_id')

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # 4. Call Procedure with EXPLICIT CASTS
            cur.execute(
                """
                CALL learning.usp_v1_start_assessment_attempt(
                    %s::integer,   -- p_assignment_id
                    %s::integer,   -- p_student_id
                    %s::varchar,   -- p_subscription_id
                    0,             -- o_status
                    ''::text,      -- o_message
                    '{}'::jsonb    -- o_data
                )
                """, 
                (assignment_id, student_id, subscription_id)
            )
            
            res = cur.fetchone()
            conn.commit()
            
            # Check response status
            if res['o_status'] == 200:
                return api_response(message=res['o_message'], data=res['o_data'], code=200, status="success")
            else:
                return api_response(message=res['o_message'], code=res['o_status'], status="error")

        except Exception as db_err:
            conn.rollback()
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")

 
# 3. Save Single Answer
def save_single_answer():
    try:
        # 1. Get User ID
        student_id, error = TokenVerifier.get_user_id()
        if error: return api_response(message=error, code=401)

        data = request.get_json()
        
        # 2. Extract Data including sl_no
        attempt_id = data.get('attempt_id')
        question_id = data.get('question_id')
        sl_no = data.get('sl_no') 
        answer = data.get('answer')
        time_taken = data.get('time_taken')

        if not all([attempt_id, question_id, answer]):
            return api_response(message="Missing required data", code=400)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # 3. Call Procedure with sl_no
            cur.execute(
                """
                CALL learning.usp_v1_save_single_answer(
                    %s, %s, %s, %s, %s, %s, 0, ''
                )
                """, 
                (
                    attempt_id, 
                    student_id, 
                    question_id, 
                    int(sl_no) if sl_no is not None else 0, 
                    str(answer), 
                    int(time_taken or 0)
                )
            )
            res = cur.fetchone()
            conn.commit()
            return api_response(message=res['o_message'], code=res['o_status'])
        finally:
            cur.close(); conn.close()
    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500)
 
# 5. Submit Assessment Result (Alternative/Batch Submit)
def submit_assessment_result():
    try:
        student_id, error = TokenVerifier.get_user_id()
        if error: return api_response(message=error, code=401)

        data = request.get_json()
        attempt_id = data.get('attempt_id')
        answers = data.get('answers') # List of {question_id, answer, time_taken}

        if not attempt_id or not answers:
            return api_response(message="Attempt ID and Answers are required", code=400)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cur.execute("CALL learning.usp_v1_submit_assessment_result(%s, %s, %s, 0, '', '{}')", 
                        (attempt_id, student_id, json.dumps(answers)))
            res = cur.fetchone()
            conn.commit()
            return api_response(message=res['o_message'], data=res['o_data'], code=res['o_status'])
        finally:
            cur.close(); conn.close()
    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500)




def finish_assessment():
    """
    POST /api/v1/learning/finish_assessment
    Body: { "attempt_id": 123 }
    """
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
                CALL learning.usp_v2_finish_assessment(
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