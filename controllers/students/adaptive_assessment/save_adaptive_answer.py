from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras
import json
import jwt 
 
def save_adaptive_answer():
    conn = None
    try:
        # 1. AUTHENTICATION
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
            
        student_id = int(user_id_str)

        # 2. GET PAYLOAD (With your new clean keys!)
        data = request.get_json()
        if not data:
            return api_response(message="Request body is empty", code=400, status="error")

        attempt_id = data.get('attempt_id')
        question_id = data.get('question_id')
        sl_no = data.get('sl_no')
        answer = data.get('answer')
        time_taken = data.get('time_taken', 0)

        if not attempt_id or not question_id or not sl_no:
            return api_response(message="attempt_id, question_id, and sl_no are required", code=400, status="error")

        # 🔥 Auto-detect if skipped (If answer is None or empty string)
        is_skipped = True if answer is None or str(answer).strip() == "" else False
        answer_text = str(answer) if not is_skipped else ""

        # 3. DATABASE CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            CALL learning.usp_save_adaptive_answer_v1(
                %s::INTEGER, %s::INTEGER, %s::INTEGER, %s::TEXT, %s::INTEGER, %s::BOOLEAN, %s::INTEGER,
                NULL, NULL, NULL
            )
        """
        
        cur.execute(query, (
            int(attempt_id), 
            student_id, 
            int(question_id), 
            answer_text,         # 🔥 Safely mapped
            int(time_taken),     # 🔥 Safely mapped
            is_skipped,          # 🔥 Auto-calculated
            int(sl_no)           # 🔥 Safely mapped
        ))
        
        result = cur.fetchone()
        conn.commit()

        res_status  = result.get('p_status', 'error')
        res_message = result.get('p_message', 'No message')
        res_data    = result.get('p_data', {})

        if res_status == 'success':
            return api_response(message=res_message, data=res_data, code=200, status="success")
        else:
            return api_response(message=res_message, code=400, status="error")

    except Exception as e:
        if conn: conn.rollback()
        print(f"CRITICAL_DEBUG: {repr(e)}") 
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: conn.close()