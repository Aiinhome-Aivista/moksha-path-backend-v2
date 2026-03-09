# # from flask import request
# # from config import get_db_connection
# # from utils.subscription_helper import get_active_subscription
# # from utils.token_helper import TokenVerifier
# # from utils.api_response import api_response
# # import psycopg2.extras
 

# # def generate_auto_plan():
# #     """
# #     POST /api/v1/learning/generate_plan
# #     Body: { "topic_ids": [1, 2] } (Optional)
# #     """
# #     try:
# #         # 1. Get User Payload from Token
# #         payload = TokenVerifier.get_user_payload() # Ensure this method exists in utils/token_helper.py
# #         if not payload:
# #             return api_response(message="Unauthorized", code=401, status="error")
            
# #         user_id = payload.get('sub')
# #         roles = payload.get('roles', [])
 
# #         user_id = int(payload.get('sub'))

# #         #  ALWAYS fetch latest subscription from DB
# #         subscription_id = get_active_subscription(user_id)

# #         if not subscription_id:
# #             return api_response(
# #                 message="Active subscription not found.",
# #                 code=403,
# #                 status="error"
# #             )
# #         data = request.get_json() or {}
        
# #         # =========================================================
# #         # CRITICAL FIX: Convert Empty List [] to None for SQL NULL
# #         # =========================================================
# #         topic_ids = data.get('topic_ids')
# #         if not topic_ids: 
# #             topic_ids = None 

# #         conn = get_db_connection()
# #         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# #         try:
# #             # 3. Call Procedure with EXPLICIT CASTS
# #             # If topic_ids is None, it passes NULL::integer[] (Which selects ALL topics)
# #             cur.execute(
# #                 """
# #                 CALL learning.usp_v1_generate_auto_study_plan(
# #                     %s::integer, 
# #                     %s::varchar, 
# #                     %s::integer[], 
# #                     0, 
# #                     ''::text, 
# #                     '{}'::jsonb
# #                 )
# #                 """,
# #                 (user_id, subscription_id, topic_ids)
# #             )
# #             result = cur.fetchone()
# #             conn.commit()

# #             if result['o_status'] == 200:
# #                 return api_response(message=result['o_message'], data=result['o_analysis'], code=200, status="success")
# #             else:
# #                 return api_response(message=result['o_message'], code=result['o_status'], status="error")

# #         except Exception as db_err:
# #             conn.rollback()
# #             return api_response(message="Database Error", error=str(db_err), code=500, status="error")
# #         finally:
# #             cur.close()
# #             conn.close()

# #     except Exception as e:
# #         return api_response(message="Server Error", error=str(e), code=500, status="error")
    

# from flask import request
# from config import get_db_connection
# from utils.subscription_helper import get_active_subscription
# from utils.token_helper import TokenVerifier
# from utils.api_response import api_response
# import psycopg2.extras

# def generate_auto_plan():
#     """
#     POST /api/v1/learning/generate_plan
#     Body: { "topic_ids": [1, 2] } (Optional)
#     """
#     try:
#         # 1. Get User Payload from Token
#         payload = TokenVerifier.get_user_payload() 
#         if not payload:
#             return api_response(message="Unauthorized", code=401, status="error")
            
#         user_id = int(payload.get('sub'))

#         # 2. ALWAYS fetch latest subscription from DB
#         subscription_id = get_active_subscription(user_id)

#         if not subscription_id:
#             return api_response(
#                 message="Active subscription not found.",
#                 code=403,
#                 status="error"
#             )
            
#         data = request.get_json() or {}
        
#         # =========================================================
#         # CRITICAL FIX: Convert Empty List [] to None for SQL NULL
#         # =========================================================
#         topic_ids = data.get('topic_ids')
#         if not topic_ids: 
#             topic_ids = None 

#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         try:
#             # 3. Call Procedure with EXPLICIT CASTS
#             cur.execute(
#                 """
#                 CALL learning.usp_v2_generate_auto_study_plan(
#                     %s::integer, 
#                     %s::varchar, 
#                     %s::integer[], 
#                     0, 
#                     ''::text, 
#                     '{}'::jsonb
#                 )
#                 """,
#                 (user_id, subscription_id, topic_ids)
#             )
            
#             result = cur.fetchone()

#            # generate default test ONLY if plan created successfully
#             if result and result.get('o_status') == 200:

#                 cur.execute(
#                     """
#                     CALL learning.usp_v1_generate_subject_default_test(
#                         %s::integer,
#                         %s::varchar
#                     )
#                     """,
#                     (user_id, subscription_id)
#                 )

#             conn.commit()

#             if result['o_status'] == 200:
#                 return api_response(message=result['o_message'], data=result['o_analysis'], code=200, status="success")
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
from utils.subscription_helper import get_active_subscription # <--- KEPT AS FAILSAFE!
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras

def generate_auto_plan():
    """
    POST /api/v1/learning/generate_plan
    Body: { "topic_ids": [1, 2] } (Optional)
    """
    try:
        # 1. Get User Payload from Token
        payload = TokenVerifier.get_user_payload() 
        if not payload:
            return api_response(message="Unauthorized", code=401, status="error")
            
        user_id = int(payload.get('sub'))

        # =========================================================================
        # 2. SMART SUBSCRIPTION HUNTER (Token First, Database Second)
        # =========================================================================
        subscription_id = None
        roles = payload.get('roles', [])
        
        # Step A: Check the Token (Perfect for Group Plans and current active sessions)
        for role in roles:
            if role.get('is_default') is True:
                subscription_id = role.get('subscription_id')
                break
        
        if not subscription_id:
            subscription_id = payload.get('sub_id') or payload.get('subscription_id')

        # Step B: FAILSAFE - Check the Database Helper!
        # (If token is stale but they just bought a new plan, this saves the day)
        if not subscription_id:
            subscription_id = get_active_subscription(user_id)

        # Step C: Final Validation
        if not subscription_id:
            return api_response(
                message="Active subscription not found.",
                code=403,
                status="error"
            )
            
        data = request.get_json() or {}
        
        # =========================================================
        # CRITICAL FIX: Convert Empty List [] to None for SQL NULL
        # =========================================================
        topic_ids = data.get('topic_ids')
        if not topic_ids: 
            topic_ids = None 

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 3. Call Procedure with EXPLICIT CASTS
            cur.execute(
                """
                CALL learning.usp_v2_generate_auto_study_plan(
                    %s::integer, 
                    %s::varchar, 
                    %s::integer[], 
                    0, 
                    ''::text, 
                    '{}'::jsonb
                )
                """,
                (user_id, subscription_id, topic_ids)
            )
            
            result = cur.fetchone()

            # generate default test ONLY if plan created successfully
            if result and result.get('o_status') == 200:
                cur.execute(
                    """
                    CALL learning.usp_v1_generate_subject_default_test(
                        %s::integer,
                        %s::varchar
                    )
                    """,
                    (user_id, subscription_id)
                )

            conn.commit()

            if result['o_status'] == 200:
                return api_response(message=result['o_message'], data=result['o_analysis'], code=200, status="success")
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