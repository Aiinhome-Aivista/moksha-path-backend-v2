from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription  # <--- Imported Helper
import psycopg2.extras


 
# ==========================================
# HELPER FUNCTION
# ==========================================
def get_user_context():
    """
    Extracts User ID from the Token and fetches the active Subscription ID from DB.
    Returns: (user_id, subscription_id, error_message)
    """
    payload = TokenVerifier.get_user_payload()
    if not payload: 
        return None, None, "Unauthorized"
    
    user_id = payload.get('sub')
    
    # ALWAYS fetch latest subscription from DB
    subscription_id = get_active_subscription(user_id)
        
    return user_id, subscription_id, None


# ==========================================
# GET STUDENT ASSESSMENTS
# ==========================================
 
# def get_student_assessments():
#     """
#     GET /api/v1/learning/student/assessments
#     """
#     try:
#         # 1. Get Context Securely from JWT
#         payload = TokenVerifier.get_user_payload()
#         if not payload: 
#             return api_response(message="Unauthorized or invalid token.", code=401, status="error")
            
#         student_id = payload.get('sub')

#         if not student_id:
#             return api_response(message="User ID not found in token.", code=401, status="error")
            
#         # =========================================================================
#         # 2. Extract Subscription ID directly from JWT (Bypassing get_user_context)
#         # =========================================================================
#         subscription_id = None
#         roles = payload.get('roles', [])
        
#         for role in roles:
#             if role.get('is_default') is True:
#                 subscription_id = role.get('subscription_id')
#                 break
        
#         if not subscription_id:
#             subscription_id = payload.get('sub_id') or payload.get('subscription_id')

#         if not subscription_id: 
#             return api_response(message="No active subscription found.", code=403, status="error")

#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         try:
#             # 3. Call Procedure (Now securely passing the subscription_id)
#             cur.execute(
#                 "CALL learning.usp_v1_get_student_assessments_new(%s, %s, 0, '', '{}'::JSONB)",
#                 (int(student_id), subscription_id)
#             )
#             result = cur.fetchone()
#             conn.commit()

#             return api_response(
#                 message=result['o_message'], 
#                 data=result['o_data'], 
#                 code=result['o_status'], 
#                 status="success"
#             )

#         except Exception as db_err:
#             conn.rollback()
#             return api_response(message="Database Error", error=str(db_err), code=500, status="error")
#         finally:
#             cur.close()
#             conn.close()

#     except Exception as e:
#         return api_response(message="Server Error", error=str(e), code=500, status="error")



 
def get_student_assessments():
    """
    GET /api/v1/learning/student/assessments
    """
    try:
        # 1. Get Context Securely from JWT
        payload = TokenVerifier.get_user_payload()
        if not payload: 
            return api_response(message="Unauthorized or invalid token.", code=401, status="error")
            
        student_id = payload.get('sub')

        if not student_id:
            return api_response(message="User ID not found in token.", code=401, status="error")
            
        # =========================================================================
        # 2. SMART SUBSCRIPTION HUNTER (Token First, Database Second)
        # =========================================================================
        subscription_id = None
        roles = payload.get('roles', [])
        
        # Step A: Check the Token
        for role in roles:
            if role.get('is_default') is True:
                subscription_id = role.get('subscription_id')
                break
        
        if not subscription_id:
            subscription_id = payload.get('sub_id') or payload.get('subscription_id')

        # Step B: FAILSAFE - Check the Database Helper!
        if not subscription_id:
            subscription_id = get_active_subscription(int(student_id))

        # Step C: Final Validation
        if not subscription_id: 
            return api_response(message="No active subscription found.", code=403, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 3. Call Procedure
            cur.execute(
                "CALL learning.usp_v1_get_student_assessments_new(%s, %s, 0, '', '{}'::JSONB)",
                (int(student_id), subscription_id)
            )
            result = cur.fetchone()
            conn.commit()

            return api_response(
                message=result['o_message'], 
                data=result['o_data'], 
                code=result['o_status'], 
                status="success"
            )

        except Exception as db_err:
            conn.rollback()
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")




# def get_student_assessments():
    """
    GET /api/v1/learning/student/assessments
    """
    try:
        # 1. Get User Context (Using the helper function)
        student_id, subscription_id, error = get_user_context()
        if error: 
            return api_response(message=error, code=401, status="error")
        
        # Security check: Prevent fetching if subscription is expired/missing
        if not subscription_id: 
            return api_response(message="No active subscription found.", code=403, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 2. Call Procedure
            # Note: I kept the parameters exactly as you provided. 
            # If your SP needs to filter by subscription_id later, you can easily add it here!
            cur.execute(
                "CALL learning.usp_v1_get_student_assessments_new(%s, 0, '', '{}'::JSONB)",
                (student_id,)
            )
            result = cur.fetchone()
            conn.commit()

            return api_response(
                message=result['o_message'], 
                data=result['o_data'], 
                code=result['o_status'], 
                status="success"
            )

        except Exception as db_err:
            conn.rollback() # Good practice to rollback on error
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")