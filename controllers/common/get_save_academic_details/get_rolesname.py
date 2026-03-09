from flask import jsonify
from config import get_db_connection
from utils.api_response import api_response

def get_all_roles():
    """
    GET /api/roles
    Fetches list of active roles using Stored Procedure.
    """
    conn = None
    try:
        conn = get_db_connection()
        # Ensure autocommit is True for Procedure calls if using certain drivers, 
        # though usually fine for simple reads. Consistency is good.
        conn.autocommit = True 
        cur = conn.cursor()
        
        # Call Stored Procedure
        cur.execute("CALL login.usp_v1_get_active_roles(NULL::JSONB, NULL::VARCHAR, NULL::INTEGER)")
        result = cur.fetchone()
        
        # The procedure returns the data already formatted as a list of dicts (JSON)
        return api_response(
            message=result['p_message'], 
            code=result['p_status_code'], 
            data=result['p_roles_json']
        )

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn:
            conn.close()