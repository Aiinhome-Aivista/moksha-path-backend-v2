
from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras
import json
import jwt   
  
def anddaptive_get_student_assessments():
    conn = None
    try:
        # =========================================================================
        # 1. AUTHENTICATION
        # =========================================================================
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
            
        student_id = int(user_id_str)

        # =========================================================================
        # 2. EXTRACT SUBSCRIPTION ID FROM CUSTOM HEADER TOKEN
        # =========================================================================
        # 🔥 Safely checks for BOTH hyphen and underscore to prevent Postman typos!
        sub_token = request.headers.get('Subscription-Id') or request.headers.get('Subscription_Id')
        
        if not sub_token:
            return api_response(message="Subscription-Id header is missing.", code=400, status="error")

        # Decode the token payload
        try:
            sub_payload = jwt.decode(sub_token, options={"verify_signature": False})
        except Exception as e:
            return api_response(message=f"Invalid subscription token: {str(e)}", code=400, status="error")

        # Find the default subscription_id
        subscription_id = None
        roles = sub_payload.get('roles', [])
        
        for role in roles:
            if role.get('is_default') is True:
                subscription_id = role.get('subscription_id')
                break
        
        # Fallback to sub_id if loop fails
        if not subscription_id:
            subscription_id = sub_payload.get('sub_id') or sub_payload.get('subscription_id')

        if not subscription_id:
             return api_response(message="Active Subscription ID not found for this user.", code=403, status="error")

        # =========================================================================
        # 3. DATABASE CALL
        # =========================================================================
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            CALL learning.usp_get_student_assessments_v1(
                %s::INTEGER, %s::TEXT, 
                NULL, NULL, NULL
            )
        """
        
        cur.execute(query, (student_id, subscription_id))
        result = cur.fetchone()
        conn.commit()

        res_status  = result.get('p_status', 'error')
        res_message = result.get('p_message', 'No message')
        res_data    = result.get('p_data', [])

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