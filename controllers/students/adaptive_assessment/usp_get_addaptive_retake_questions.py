from flask import Blueprint, request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription  
import psycopg2         
import psycopg2.extras   
import json
 
def start_adaptive_retake():
    conn = None
    try:
        # 1. AUTHENTICATION
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
            
        student_id = int(user_id_str)

        # 2. GET PAYLOAD
        data = request.get_json()
        if not data or 'assignment_id' not in data:
            return api_response(message="assignment_id is required", code=400, status="error")

        old_assignment_id = data.get('assignment_id')

        # 3. GET SUBSCRIPTION
        subscription_id = get_active_subscription(student_id)
        if not subscription_id:
             return api_response(message="No active subscription found", code=403, status="error")

        # 4. DATABASE CALL
        conn = get_db_connection()
        # Explicitly using psycopg2.extras.RealDictCursor
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            CALL learning.usp_start_adaptive_retake_assessment(
                %s::INTEGER, %s::INTEGER, %s::VARCHAR,
                NULL, NULL, NULL
            )
        """
        
        cur.execute(query, (int(old_assignment_id), student_id, subscription_id))
        result = cur.fetchone()
        conn.commit()

        # Extracting based on the INOUT parameter names in your SP
        res_status  = result.get('o_status')
        res_message = result.get('o_message', 'No message')
        res_data    = result.get('o_data', {})

        if res_status == 200:
            return api_response(message=res_message, data=res_data, code=200, status="success")
        else:
            return api_response(message=res_message, code=res_status or 400, status="error")

    except Exception as e:
        if conn: conn.rollback()
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: conn.close()