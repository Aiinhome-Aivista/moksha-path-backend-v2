from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras

# ==========================================
# SECURITY HELPER
# ==========================================
def _verify_and_get_student_context():
    """
    Extracts parent token, validates student_id from the query parameter, 
    and ensures the parent successfully invited this child via subscription_invites.
    """
    parent_id_str, auth_error = TokenVerifier.get_user_id()
    if not parent_id_str:
        return None, None, f"Unauthorized: {auth_error}"
    
    parent_id = int(parent_id_str)
    
    payload = TokenVerifier.get_user_payload()
    subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
    
    if not subscription_id:
        return None, None, "No active subscription found in token. Please switch profile."

    student_id = request.args.get('student_id', type=int)
    if not student_id:
        return None, None, "student_id parameter is required for this dashboard."

    # SECURITY CHECK: Did this parent invite this child, and did the child accept?
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # FIX: Updated column names to sender_user_id and receiver_user_id
        cur.execute("""
            SELECT 1 FROM subscription.subscription_invites 
            WHERE sender_user_id = %s AND receiver_user_id = %s AND subscription_code = %s AND status = 'Accepted'
        """, (parent_id, student_id, subscription_id))
        
        if not cur.fetchone():
            return None, None, "Forbidden: You are not authorized to view this student's data for this subscription."
    except Exception as e:
        return None, None, f"DB Error: {str(e)}"
    finally:
        if conn: conn.close()
        
    return student_id, subscription_id, None


def _call_student_kpi_sp(sp_name):
    """Generic caller that executes the Student SP on behalf of the Parent."""
    conn = None
    try:
        student_id, subscription_id, err = _verify_and_get_student_context()
        if err:
            return api_response(message=err, code=403 if "Forbidden" in err else 400, status="error")

        conn = get_db_connection()
        
        if sp_name == 'learning.sp_v1_check_exam_readiness':
            conn.autocommit = True
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(f"CALL {sp_name}(%s::INTEGER, %s::TEXT, NULL::TEXT, NULL::TEXT, NULL::JSONB)", (student_id, subscription_id))
            result = cur.fetchone()
            if not result: return api_response(message="No DB Response", code=500, status="error")
            
            p_status, p_message, p_data = result.get('p_status'), result.get('p_message'), result.get('p_data')
            status_code = 403 if p_status == "limit_reached" else (400 if p_status == "error" else 200)
            return api_response(message=p_message, code=status_code, status=p_status, data=p_data)
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(f"CALL {sp_name}(%s, %s, NULL, NULL, NULL)", (student_id, subscription_id))
        result = cur.fetchone()
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()


# ==========================================
# PARENT DASHBOARD APIs
# ==========================================

# 1. API for the Dropdown Menu
def get_parent_children_dropdown():
    """ GET /api/v1/parent_teacher/dashboard/parent/children """
    conn = None
    try:
        parent_id_str, auth_error = TokenVerifier.get_user_id()
        if not parent_id_str: return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        payload = TokenVerifier.get_user_payload()
        subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
        
        if not subscription_id: return api_response(message="No active subscription found.", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("CALL learning.sp_v1_get_parent_children_list(%s, %s, NULL, NULL, NULL)", (int(parent_id_str), subscription_id))
        result = cur.fetchone()
        
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()


# 2. KPI APIs (All require ?student_id=XXX)
def get_parent_subject_confidence():
    return _call_student_kpi_sp('learning.usp_v1_get_subject_confidence')

def get_parent_progressing_ability():
    return _call_student_kpi_sp('learning.usp_v1_get_progressing_ability')

def get_parent_consistency_score():
    return _call_student_kpi_sp('learning.usp_v1_get_consistency_score')

def get_parent_exam_readiness():
    return _call_student_kpi_sp('learning.sp_v1_check_exam_readiness')

def get_parent_pending_tasks():
    return _call_student_kpi_sp('learning.sp_v1_get_learning_pending_tasks')

def get_parent_subjectwise_average_score():
    return _call_student_kpi_sp('learning.sp_v1_get_subjectwise_average_score')

def get_parent_student_subjects():
    return _call_student_kpi_sp('learning.sp_get_student_subjects')

def get_parent_student_strength_weakness():
    return _call_student_kpi_sp('learning.sp_v1_get_student_strength_weakness')