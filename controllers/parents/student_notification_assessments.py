# from flask import request
# from config import get_db_connection
# from utils.api_response import api_response
# from utils.token_helper import TokenVerifier
# import psycopg2.extras

# def get_student_notification_assessments():
#     """
#     GET /api/v1/student/assessments
#     Fetches all assessments assigned to the logged-in student (Notifications Dashboard).
#     """
#     try:
#         # 1. Get Context Securely from JWT
#         payload = TokenVerifier.get_user_payload()
#         if not payload: 
#             return api_response(message="Unauthorized or invalid token.", code=401, status="error")
            
#         student_id = payload.get('sub')
#         subscription_id = payload.get('sub_id') or payload.get('subscription_id') or payload.get('sid')

#         if not student_id:
#             return api_response(message="User ID not found in token.", code=401, status="error")
#         if not subscription_id: 
#             return api_response(message="No active subscription found.", code=403, status="error")

#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         try: 
#             # 2. Call the Student Assessments Stored Procedure
#             cur.execute(
#                 """
#                 CALL learning.usp_v1_get_student_notification_assessments(
#                     %s, %s, 0, '', '{}'::jsonb
#                 )
#                 """,
#                 (int(student_id), subscription_id)
#             )
#             result = cur.fetchone()
#             conn.commit()

#             # 3. Return the JSON structure
#             if result['o_status'] == 200:
#                 return api_response(message=result['o_message'], data=result['o_data'], code=200, status="success")
#             else:
#                 return api_response(message=result['o_message'], code=result['o_status'], status="error")

#         except Exception as db_err:
#             conn.rollback()
#             return api_response(message="Database Error", error=str(db_err), code=500, status="error")
#         finally:
#             cur.close()
#             conn.close()

#     except Exception as e:
#         return api_response(message="Server Error", error=str(e), code=500, status="error")



from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
from utils.subscription_helper import get_active_subscription  # <-- NEW IMPORT
import psycopg2.extras



def get_student_notification_assessments():
    """
    GET /api/v1/student/assessments
    Fetches all assessments assigned to the logged-in student (Notifications Dashboard).
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
        # 2. Extract Subscription ID from the Default Role in JWT Payload
        # =========================================================================
        subscription_id = None
        roles = payload.get('roles', [])
        
        # Hunt for the default role and grab its specific subscription ID
        for role in roles:
            if role.get('is_default') is True:
                subscription_id = role.get('subscription_id')
                break
        
        # Fallback mechanisms just in case the roles array is malformed
        if not subscription_id:
            subscription_id = payload.get('sub_id') or payload.get('subscription_id')

        if not subscription_id: 
            return api_response(message="No active subscription found.", code=403, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try: 
            # 3. Call the Student Assessments Stored Procedure
            cur.execute(
                """
                CALL learning.usp_v1_get_student_notification_assessments(
                    %s, %s, 0, '', '{}'::jsonb
                )
                """,
                (int(student_id), subscription_id)
            )
            result = cur.fetchone()
            conn.commit()

            # 4. Return the JSON structure
            if result['o_status'] == 200:
                return api_response(message=result['o_message'], data=result['o_data'], code=200, status="success")
            else:
                return api_response(message=result['o_message'], code=result['o_status'], status="error")

        except Exception as db_err:
            conn.rollback()
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error") 