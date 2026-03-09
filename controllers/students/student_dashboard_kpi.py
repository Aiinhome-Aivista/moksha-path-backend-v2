from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras

# 1. Subject Confidence Slider
def get_subject_confidence():
    """ GET /api/v1/analytics/confidence """
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        # Extract subscription_id securely from token payload
        payload = TokenVerifier.get_user_payload()
        subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
        
        if not subscription_id: 
            return api_response(message="No active subscription found in token. Please switch profile.", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("CALL learning.usp_v1_get_subject_confidence(%s, %s, NULL, NULL, NULL)", (int(user_id_str), subscription_id))
        result = cur.fetchone()

        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()


# 2. Progressing Ability
def get_progressing_ability():
    """ GET /api/v1/analytics/progressing-ability """
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        payload = TokenVerifier.get_user_payload()
        subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
        
        if not subscription_id: 
            return api_response(message="No active subscription found in token. Please switch profile.", code=400, status="error")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("CALL learning.usp_v1_get_progressing_ability(%s, %s, NULL, NULL, NULL)", (int(user_id_str), subscription_id))
        result = cur.fetchone()

        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()


# 3. Consistency Score
def get_consistency_score():
    """ GET /api/v1/analytics/consistency """
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        payload = TokenVerifier.get_user_payload()
        subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
        
        if not subscription_id: 
            return api_response(message="No active subscription found in token. Please switch profile.", code=400, status="error")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("CALL learning.usp_v1_get_consistency_score(%s, %s, NULL, NULL, NULL)", (int(user_id_str), subscription_id))
        result = cur.fetchone()

        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()


def get_exam_readiness():
    """ GET /api/v1/analytics/exam-readiness """
    conn = None
    try:
        user_id_raw, auth_error = TokenVerifier.get_user_id()
        if not user_id_raw:
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        # 1. ADD THIS: Extract subscription_id from token
        payload = TokenVerifier.get_user_payload()
        subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
        
        if not subscription_id: 
            return api_response(message="No active subscription found. Please switch profile.", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 2. UPDATE THIS: Pass subscription_id to the Stored Procedure
        cur.execute("""
            CALL learning.sp_v1_check_exam_readiness(
                %s::INTEGER, 
                %s::TEXT, 
                NULL::TEXT, 
                NULL::TEXT, 
                NULL::JSONB
            )
        """, (int(user_id_raw), subscription_id))

        result = cur.fetchone()

        if not result:
            return api_response(message="No DB Response", code=500, status="error")

        # Result processing
        p_status = result.get('p_status')
        p_message = result.get('p_message')
        p_data = result.get('p_data')

        status_code = 200
        if p_status == "limit_reached":
            status_code = 403 
        elif p_status == "error":
            status_code = 400 

        return api_response(message=p_message, code=status_code, status=p_status, data=p_data)

    except Exception as e:
        print("PYTHON LOG ERROR:", str(e))
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))
    finally:
        if conn: conn.close()



# def get_exam_readiness():
#     conn = None
#     try:
        
#         user_id_raw, auth_error = TokenVerifier.get_user_id()
#         if not user_id_raw:
#             return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        
#         user_id = int(user_id_raw)

#         # DB connection with RealDictCursor
#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         # DB procedure call (sp_check_exam_readiness) - parameter hishebe user_id pathano hocche
#         # Explicitly Casting types jate Postgres 'Not Unique' error na dey
#         cur.execute("""
#             CALL learning.sp_check_exam_readiness(
#                 %s::INTEGER, 
#                 NULL::TEXT, 
#                 NULL::TEXT, 
#                 NULL::JSONB
#             )
#         """, (user_id,))

#         result = cur.fetchone()

#         if not result:
#             return api_response(message="No DB Response", code=500, status="error")

#         # Result processing (SP theke p_status, p_message, p_data asbe)
#         p_status = result.get('p_status')
#         p_message = result.get('p_message')
#         p_data = result.get('p_data')

#         # Business logic mapping for API status codes
#         status_code = 200
#         if p_status == "limit_reached":
#             status_code = 403 # Forbidden
#         elif p_status == "error":
#             status_code = 400 # Bad Request

#         return api_response(
#             message=p_message,
#             code=status_code,
#             status=p_status,
#             data=p_data
#         )

#     except Exception as e:
#         print("PYTHON LOG ERROR:", str(e))
#         return api_response(
#             message="Internal Server Error", 
#             code=500, 
#             status="error", 
#             error=str(e)
#         )
#     finally:
#         if conn:
#             conn.close()


def get_pending_tasks():
    """ GET /api/v1/learning/student/pending-tasks """
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        # Securely grab the active subscription from the token
        payload = TokenVerifier.get_user_payload()
        subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
        
        if not subscription_id: 
            return api_response(message="No active subscription found. Please switch profile.", code=400, status="error")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Call our new Stored Procedure
        cur.execute("CALL learning.sp_v1_get_learning_pending_tasks(%s, %s, NULL, NULL, NULL)", (int(user_id_str), subscription_id))
        result = cur.fetchone()

        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()


def get_subjectwise_average_score():
    """ GET /api/v1/learning/analytics/subject-average-score """
    conn = None
    try:
        # 1. Authenticate User
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        # 2. Extract Active Subscription from Token
        payload = TokenVerifier.get_user_payload()
        subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
        
        if not subscription_id: 
            return api_response(message="No active subscription found in token. Please switch profile.", code=400, status="error")
        
        # 3. Call DB Procedure
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("CALL learning.sp_v1_get_subjectwise_average_score(%s, %s, NULL, NULL, NULL)", (int(user_id_str), subscription_id))
        result = cur.fetchone()

        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 5. Get Active Subjects
def get_student_subjects():
    """ GET /api/v1/learning/student/subjects """
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        # Grab Active Subscription
        payload = TokenVerifier.get_user_payload()
        subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
        
        if not subscription_id: 
            return api_response(message="No active subscription found. Please switch profile.", code=400, status="error")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Execute SP
        cur.execute("CALL learning.sp_get_student_subjects(%s, %s, NULL, NULL, NULL)", (int(user_id_str), subscription_id))
        result = cur.fetchone()

        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

def get_student_strength_weakness():
    """ GET /api/v1/learning/analytics/strength-weakness """
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        # Grab Active Subscription
        payload = TokenVerifier.get_user_payload()
        subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
        
        if not subscription_id: 
            return api_response(message="No active subscription found. Please switch profile.", code=400, status="error")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Execute SP
        cur.execute("CALL learning.sp_v1_get_student_strength_weakness(%s, %s, NULL, NULL, NULL)", (int(user_id_str), subscription_id))
        result = cur.fetchone()

        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()