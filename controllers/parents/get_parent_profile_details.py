from flask import request
from config import get_db_connection
from controllers.teachers.teacher_dashboard_controller import _get_teacher_context
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras

# 9. Parent Profile Details (Name, School, Class)
def get_parent_profile_details():
    """ GET /api/v1/parent/dashboard/parent-profile """
    conn = None
    try:
        parent_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("CALL learning.usp_v1_parent_profile_details(%s, %s, NULL, NULL, NULL)", (parent_id, subscription_id))
        result = cur.fetchone()
        
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

