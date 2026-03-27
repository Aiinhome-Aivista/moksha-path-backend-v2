
from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras
import json
import jwt 
  
def get_next_adaptive_question():
    conn = None
    try:
        # 1. AUTHENTICATION
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
            
        student_id = int(user_id_str)
        attempt_id = request.args.get('attempt_id')

        if not attempt_id:
            return api_response(message="attempt_id is required as a query parameter", code=400, status="error")

        # 2. DATABASE CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Added ::BIGINT to handle high-volume student IDs
        query = """
            CALL learning.usp_get_next_adaptive_question_v1(
                %s::INTEGER, 
                %s::BIGINT, 
                NULL, NULL, NULL
            )
        """
        
        # Passing student_id as the second argument for the filter logic
        cur.execute(query, (int(attempt_id), student_id))
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
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: conn.close()