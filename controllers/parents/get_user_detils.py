# from flask import request
# from config import get_db_connection
# from utils.api_response import api_response
# from utils.token_helper import TokenVerifier  # <-- Changed Import
# import psycopg2.extras

# def get_academic_hierarchy():
#     """
#     GET /api/v1/master/academic-hierarchy
#     Fetches Board, Class, Sections, Subjects, Chapters, and Topics based on User Mapping & Subscription.
#     """
#     try:
#         # 1. Get Context Securely from JWT using existing TokenVerifier
#         payload = TokenVerifier.get_user_payload()
        
#         if not payload: 
#             return api_response(message="Unauthorized or invalid token.", code=401, status="error")
            
#         # Extract variables exactly as they are named in your TokenGenerator
#         user_id = payload.get('sub')
#         subscription_id = payload.get('sub_id') or payload.get('subscription_id') or payload.get('sid')

#         # Validation
#         if not user_id:
#             return api_response(message="User ID not found in token.", code=401, status="error")
#         if not subscription_id: 
#             return api_response(message="No active subscription found.", code=403, status="error")

#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         try: 
#             # 2. Call the Stored Procedure
#             cur.execute(
#                 """
#                 CALL master.usp_v1_get_teacher_assignment_hierarchy(
#                     %s, %s, 0, '', '{}'::jsonb
#                 )
#                 """,
#                 (int(user_id), subscription_id)
#             )
#             result = cur.fetchone()
#             conn.commit()

#             # 3. Return the nested JSON structure directly
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
from utils.subscription_helper import get_active_subscription # <-- NEW IMPORT
import psycopg2.extras

def get_academic_hierarchy():
    """
    GET /api/v1/master/academic-hierarchy
    Fetches Board, Class, Sections, Subjects, Chapters, and Topics based on User Mapping & Subscription.
    """
    try:
        # 1. Get Context Securely from JWT using existing TokenVerifier
        payload = TokenVerifier.get_user_payload()
        
        if not payload: 
            return api_response(message="Unauthorized or invalid token.", code=401, status="error")
            
        user_id = payload.get('sub')

        # Validation for user_id
        if not user_id:
            return api_response(message="User ID not found in token.", code=401, status="error")
            
        # =========================================================================
        # 2. Fetch Subscription dynamically using your Helper Function
        # =========================================================================
        subscription_id = get_active_subscription(int(user_id))

        if not subscription_id: 
            return api_response(message="No active subscription found.", code=403, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try: 
            # 3. Call the Stored Procedure
            cur.execute(
                """
                CALL master.usp_v1_get_teacher_assignment_hierarchy(
                    %s, %s, 0, '', '{}'::jsonb
                )
                """,
                (int(user_id), subscription_id)
            )
            result = cur.fetchone()
            conn.commit()

            # 4. Return the nested JSON structure directly
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