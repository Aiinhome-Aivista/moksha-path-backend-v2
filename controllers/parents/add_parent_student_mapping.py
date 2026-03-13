from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier  
import psycopg2.extras


def add_parent_student_mapping():
    conn = None
    try:
        # ==========================================
        # 1. AUTHENTICATION CHECK
        # ==========================================
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        logged_in_user_id = int(user_id_str)

        # ==========================================
        # 2. PAYLOAD VALIDATION
        # ==========================================
        data = request.get_json()
        if not data:
            return api_response(message="Request body is empty", code=400, status="error")

        p_id = int(data.get('parent_user_id', 0))
        s_id = int(data.get('student_user_id', 0))

        if p_id == 0 or s_id == 0:
            return api_response(message="Parent and Student IDs are required", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # ==========================================
        # 3. CALL PROCEDURE
        # ==========================================
        # Procedure signature: (logged_in_user_id, parent_id, student_id, out_status, out_msg, out_data)
        query = """
            CALL common.usp_addparents_tudent_mapping_v1(
                %s::INTEGER, %s::INTEGER, %s::INTEGER, 
                NULL, NULL, NULL
            )
        """
        cur.execute(query, (logged_in_user_id, p_id, s_id))
        
        result = cur.fetchone()

        if not result:
            return api_response(message="Database returned no response", code=404, status="error")

        # Handle DictCursor response
        res_status  = result.get('p_status', 'error')
        res_message = result.get('p_message', 'No message')
        res_data    = result.get('p_data', None)

        # ==========================================
        # 4. RESPONSE HANDLING
        # ==========================================
        if res_status == 'success':
            return api_response(message=res_message, data=res_data, code=200, status="success")
        else:
            return api_response(message=res_message, data=res_data, code=400, status="error")

    except Exception as e:
        print(f"CRITICAL_DEBUG: {repr(e)}") 
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: 
            conn.close()