from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription  # <--- Imported Helper
import psycopg2.extras
import json

# ==========================================
# HELPER FUNCTION (Updated to use DB Helper)
# ==========================================
def get_user_context():
    """
    Extracts User ID from the Token and fetches the active Subscription ID from DB.
    Returns: (user_id, subscription_id, error_message)
    """
    payload = TokenVerifier.get_user_payload()
    if not payload: 
        return None, None, "Unauthorized"
    
    user_id = payload.get('sub')
    
    # <--- ALWAYS fetch latest subscription from DB --->
    subscription_id = get_active_subscription(user_id)
        
    return user_id, subscription_id, None

# ==========================================
# 1. Start Assessment
# ==========================================
def start_assessment_attempt():
    try:
        user_id, subscription_id, error = get_user_context()
        if error: return api_response(message=error, code=401)
        if not subscription_id: return api_response(message="No active subscription found.", code=403)

        data = request.get_json()
        assignment_id = data.get('assignment_id')

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Calls the Start Procedure
            cur.execute(
                "CALL learning.usp_v1_start_assessment_attempt(%s, %s, %s, 0, '', '{}')", 
                (assignment_id, user_id, subscription_id)
            )
            res = cur.fetchone()
            conn.commit()
            return api_response(message=res['o_message'], data=res['o_data'], code=res['o_status'])
        finally:
            cur.close(); conn.close()
    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500)

# ==========================================
# 2. Retake Assessment (SEPARATE API)
# ==========================================
def retake_assessment():
    try:
        user_id, subscription_id, error = get_user_context()
        if error: return api_response(message=error, code=401)
        if not subscription_id: return api_response(message="No active subscription found.", code=403)

        data = request.get_json()
        assignment_id = data.get('assignment_id')

        if not assignment_id:
            return api_response(message="Assignment ID is required", code=400)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Calls the SEPARATE Retake Procedure
            cur.execute(
                "CALL learning.usp_v1_retake_assessment(%s, %s, %s, 0, '', '{}')", 
                (assignment_id, user_id, subscription_id)
            )
            res = cur.fetchone()
            conn.commit()
            return api_response(message=res['o_message'], data=res['o_data'], code=res['o_status'])
        finally:
            cur.close(); conn.close()
    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500)

# ==========================================
# 3. Save Single Answer
# ==========================================
def save_single_answer():
    try:
        user_id, subscription_id, error = get_user_context()
        if error: return api_response(message=error, code=401)

        data = request.get_json()
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
            cur.execute(
                "CALL learning.usp_v1_save_single_answer(%s, %s, %s, %s, %s, %s, 0, '')", 
                (
                    attempt_id, 
                    user_id, 
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

# ==========================================
# 4. Finish Assessment
# ==========================================
def finish_assessment():
    try:
        user_id, subscription_id, error = get_user_context()
        if error: return api_response(message=error, code=401)

        data = request.get_json()
        attempt_id = data.get('attempt_id')

        if not attempt_id:
            return api_response(message="Attempt ID is required", code=400)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cur.execute(
                "CALL learning.usp_v1_finish_assessment(%s, %s, 0, '', '{}')", 
                (attempt_id, user_id)
            )
            res = cur.fetchone()
            conn.commit()
            return api_response(message=res['o_message'], data=res['o_data'], code=res['o_status'])
        finally:
            cur.close(); conn.close()
    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500)