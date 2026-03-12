from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier  
import psycopg2.extras

 
def get_institute_hierarchy():
    conn = None
    try:
        # ==========================================
        # 1. AUTHENTICATION CHECK
        # ==========================================
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        logged_in_user_id = int(user_id_str)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # ==========================================
        # 2. Call the Stored Procedure
        # ==========================================
        cur.execute("""
            CALL master.sp_get_institute_hierarchy(
                %s, NULL, NULL, NULL
            )
        """, (logged_in_user_id,))
        
        result = cur.fetchone()

        # ==========================================
        # 3. Handle Response
        # ==========================================
        if result and result.get('p_status') == 'success':
            return api_response(
                message=result.get('p_message'), 
                code=200, 
                status="success",
                data=result.get('p_data', [])
            )
        else:
            return api_response(
                message=result.get('p_message', 'Failed to fetch hierarchy'), 
                code=400, 
                status="error"
            )

    except Exception as e:
        return api_response(
            message="Internal Server Error", 
            code=500, 
            status="error", 
            error=str(e)
        )
    finally:
        if conn: 
            conn.close()