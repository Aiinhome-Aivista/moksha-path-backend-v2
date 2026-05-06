import psycopg2
from utils.token_helper import TokenVerifier
from config import get_db_connection
from utils import api_response


def _get_teacher_context():
    """Helper to extract teacher_id and subscription_id from token payload"""
    payload = TokenVerifier.get_user_payload()
    if not payload:
        return None, None, "Unauthorized: Invalid token"
    
    teacher_id = payload.get('sub')
    subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
    
    if not teacher_id:
        return None, None, "Unauthorized: Missing user identity."
    if not subscription_id:
        return None, None, "Unauthorized: No active subscription found in token. Please switch profile."
    
    return int(teacher_id), subscription_id, None


# getting profile details for dashboard

def get_teacher_profile_details():
    """ GET /api/v1/parent_teacher/dashboard/teacher-profile """
    conn = None
    try:
        teacher_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("CALL learning.sp_v1_teacher_profile_details(%s, %s, NULL, NULL, NULL)", (teacher_id, subscription_id))
        result = cur.fetchone()
        
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

