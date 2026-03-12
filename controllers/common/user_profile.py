# from flask import request
# from config import get_db_connection
# from utils.api_response import api_response
# from utils.token_helper import TokenVerifier, TokenGenerator
# import psycopg2.extras

# # 1. GET PROFILES
# # def get_user_profiles():
# #     conn = None
# #     try:
# #         user_id_str, auth_error = TokenVerifier.get_user_id()
# #         if not user_id_str: 
# #             return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
# #         user_id = int(user_id_str)
# #         conn = get_db_connection()
# #         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# #         cur.execute(
# #             "CALL login.usp_v1_get_linked_profiles(%s, NULL, NULL, NULL)", 
# #             (user_id,)
# #         )
# #         result = cur.fetchone()

# #         if result and result['p_status_code'] == 200:
# #             return api_response(
# #                 message=result['p_message'], 
# #                 code=200, 
# #                 status="success",
# #                 data=result['p_profiles']
# #             )
        
# #         return api_response(message=result.get('p_message', 'Error'), code=result.get('p_status_code', 400), status="error")

# #     except Exception as e:
# #         return api_response(message=str(e), code=500, status="error")
# #     finally:
# #         if conn: conn.close()

# # 1. GET PROFILES
# def get_user_profiles():
#     conn = None
#     try:
#         user_id_str, auth_error = TokenVerifier.get_user_id()
#         if not user_id_str: 
#             return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
#         user_id = int(user_id_str)
#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         cur.execute(
#             "CALL login.usp_v1_get_linked_profiles(%s, NULL, NULL, NULL)", 
#             (user_id,)
#         )
#         result = cur.fetchone()

#         if result and result['p_status_code'] == 200:
#             all_profiles = result['p_profiles']
            
#             # --- ADD THIS FILTER ---
#             # Only keep profiles where user_id matches the logged-in user_id
#             own_profiles_only = [p for p in all_profiles if p.get('user_id') == user_id]
            
#             return api_response(
#                 message=result['p_message'], 
#                 code=200, 
#                 status="success",
#                 data=own_profiles_only  # Return the filtered list
#             )
        
#         return api_response(message=result.get('p_message', 'Error'), code=result.get('p_status_code', 400), status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()
# # 2. SWITCH PROFILE
# # controllers/common/user_profile.py

# # def switch_profile():
# #     conn = None
# #     try:
# #         # A. Auth Check
# #         user_id_str, auth_error = TokenVerifier.get_user_id()
# #         if not user_id_str: return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
# #         requester_id = int(user_id_str)
        
# #         data = request.get_json() or {}
# #         target_profile_id = data.get('profile_id')

# #         if not target_profile_id: return api_response(message="profile_id required", code=400, status="error")

# #         conn = get_db_connection()
# #         conn.autocommit = True
# #         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# #         # B. Call Updated SP (Now expecting more OUT params)
# #         cur.execute(
# #             """
# #             CALL login.usp_v1_switch_linked_profile(
# #                 %s, %s, 
# #                 NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
# #             )
# #             """, 
# #             (requester_id, target_profile_id)
# #         )
# #         result = cur.fetchone()

# #         if result['p_status_code'] == 200:
            
# #             # C. Generate RICH Token
# #             # We pass the extra details we just got from DB
# #             new_token = TokenGenerator.generate_profile_token(
# #                 user_id=result['p_new_user_id'],
# #                 profile_id=target_profile_id,
# #                 role_id=result.get('p_role_id'),           # <-- include numeric ID
# #                 role_name=result['p_role_name'], 
# #                 institute_id=result['p_institute_id'],
                
# #                 # NEW FIELDS FOR TOKEN
# #                 username=result['p_username'],
# #                 full_name=result['p_full_name'],
# #                 subscription_id=result['p_subscription_code']
# #             )
            
# #             return api_response(
# #                 message=result['p_message'], 
# #                 code=200, 
# #                 status="success",
# #                 data={
# #                     "token": new_token,
# #                     "active_profile": {
# #                         "user_id": result['p_new_user_id'],
# #                         "username": result['p_username'],       # Send to UI
# #                         "full_name": result['p_full_name'],     # Send to UI
# #                         "profile_id": target_profile_id,
# #                         "role": result['p_role_name'],
# #                         "is_default": 1,
# #                         "subscription_id": result['p_subscription_code'], # Send to UI
# #                         "plan": result['p_subscription_info']
# #                     }
# #                 }
# #             )
        
# #         return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

# #     except Exception as e:
# #         return api_response(message=str(e), code=500, status="error")
# #     finally:
# #         if conn: conn.close()

# def switch_profile():
#     conn = None
#     try:
#         # 1. Grab old token payload to preserve "sid" (Session ID)
#         old_token_payload = TokenVerifier.get_user_payload()
#         old_sid = old_token_payload.get('sid') if old_token_payload else None

#         # 2. Auth Check
#         user_id_str, auth_error = TokenVerifier.get_user_id()
#         if not user_id_str:
#             return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
#         requester_id = int(user_id_str)
        
#         # extract contact info from the incoming token so we can carry it forward
#         prev_email = token_payload.get('email') if token_payload else None
#         prev_mobile = token_payload.get('mobile') if token_payload else None

#         data = request.get_json() or {}
#         target_profile_id = data.get('profile_id')

#         if not target_profile_id: return api_response(message="profile_id required", code=400, status="error")

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         # 3. Call SP (Expecting 13 OUT params -> 13 NULLs)
#         cur.execute(
#             """
#             CALL login.usp_v2_switch_linked_profile(
#                 %s, %s, 
#                 NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
#             )
#             """, 
#             (requester_id, target_profile_id)
#         )
#         result = cur.fetchone()

#         if result['p_status_code'] == 200:
            
#             # 4. Generate Token matching exactly the login format
#             new_token = TokenGenerator.generate_profile_token(
#                 user_id=result['p_new_user_id'],
#                 email=result.get('p_email'),
#                 mobile=result.get('p_mobile'),
#                 name=result['p_full_name'],
#                 username=result['p_username'],
#                 role_id=result.get('p_role_id'),           
#                 roles=result.get('p_roles', []),
#                 sid=old_sid,                          # Carried over from old token
#                 sub_id=result['p_subscription_code']  # The active subscription ID
#             )
            
#             return api_response(
#                 message=result['p_message'], 
#                 code=200, 
#                 status="success",
#                 data={
#                     "token": new_token,
#                     "active_profile": {
#                         "user_id": result['p_new_user_id'],
#                         "username": result['p_username'],       
#                         "full_name": result['p_full_name'],     
#                         "profile_id": target_profile_id,
#                         "role": result['p_role_name'],
#                         "is_default": 1,
#                         "subscription_id": result['p_subscription_code'], 
#                         "plan": result['p_subscription_info']
#                     }
#                 }
#             )
        
#         return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()

from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier, TokenGenerator
import psycopg2.extras

# 1. GET PROFILES
# def get_user_profiles():
#     conn = None
#     try:
#         user_id_str, auth_error = TokenVerifier.get_user_id()
#         if not user_id_str: 
#             return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
#         user_id = int(user_id_str)
#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         cur.execute(
#             "CALL login.usp_v1_get_linked_profiles(%s, NULL, NULL, NULL)", 
#             (user_id,)
#         )
#         result = cur.fetchone()

#         if result and result['p_status_code'] == 200:
#             return api_response(
#                 message=result['p_message'], 
#                 code=200, 
#                 status="success",
#                 data=result['p_profiles']
#             )
        
#         return api_response(message=result.get('p_message', 'Error'), code=result.get('p_status_code', 400), status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()

# 1. GET PROFILES
def get_user_profiles():
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        user_id = int(user_id_str)
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            "CALL login.usp_v1_get_linked_profiles(%s, NULL, NULL, NULL)", 
            (user_id,)
        )
        result = cur.fetchone()

        if result and result['p_status_code'] == 200:
            all_profiles = result['p_profiles']
            
            # --- ADD THIS FILTER ---
            # Only keep profiles where user_id matches the logged-in user_id
            own_profiles_only = [p for p in all_profiles if p.get('user_id') == user_id]
            
            return api_response(
                message=result['p_message'], 
                code=200, 
                status="success",
                data=own_profiles_only  # Return the filtered list
            )
        
        return api_response(message=result.get('p_message', 'Error'), code=result.get('p_status_code', 400), status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()
# 2. SWITCH PROFILE
# controllers/common/user_profile.py

# def switch_profile():
#     conn = None
#     try:
#         # A. Auth Check
#         user_id_str, auth_error = TokenVerifier.get_user_id()
#         if not user_id_str: return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
#         requester_id = int(user_id_str)
        
#         data = request.get_json() or {}
#         target_profile_id = data.get('profile_id')

#         if not target_profile_id: return api_response(message="profile_id required", code=400, status="error")

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         # B. Call Updated SP (Now expecting more OUT params)
#         cur.execute(
#             """
#             CALL login.usp_v1_switch_linked_profile(
#                 %s, %s, 
#                 NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
#             )
#             """, 
#             (requester_id, target_profile_id)
#         )
#         result = cur.fetchone()

#         if result['p_status_code'] == 200:
            
#             # C. Generate RICH Token
#             # We pass the extra details we just got from DB
#             new_token = TokenGenerator.generate_profile_token(
#                 user_id=result['p_new_user_id'],
#                 profile_id=target_profile_id,
#                 role_id=result.get('p_role_id'),           # <-- include numeric ID
#                 role_name=result['p_role_name'], 
#                 institute_id=result['p_institute_id'],
                
#                 # NEW FIELDS FOR TOKEN
#                 username=result['p_username'],
#                 full_name=result['p_full_name'],
#                 subscription_id=result['p_subscription_code']
#             )
            
#             return api_response(
#                 message=result['p_message'], 
#                 code=200, 
#                 status="success",
#                 data={
#                     "token": new_token,
#                     "active_profile": {
#                         "user_id": result['p_new_user_id'],
#                         "username": result['p_username'],       # Send to UI
#                         "full_name": result['p_full_name'],     # Send to UI
#                         "profile_id": target_profile_id,
#                         "role": result['p_role_name'],
#                         "is_default": 1,
#                         "subscription_id": result['p_subscription_code'], # Send to UI
#                         "plan": result['p_subscription_info']
#                     }
#                 }
#             )
        
#         return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()

# def switch_profile():
#     conn = None
#     try:
#         # 1. Grab old token payload to preserve "sid" (Session ID)
#         old_token_payload = TokenVerifier.get_user_payload()
#         old_sid = old_token_payload.get('sid') if old_token_payload else None

#         # 2. Auth Check
#         user_id_str, auth_error = TokenVerifier.get_user_id()
#         if not user_id_str: return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
#         requester_id = int(user_id_str)
        
#         data = request.get_json() or {}
#         target_profile_id = data.get('profile_id')

#         if not target_profile_id: return api_response(message="profile_id required", code=400, status="error")

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         # 3. Call SP (Expecting 13 OUT params -> 13 NULLs)
#         cur.execute(
#             """
#             CALL login.usp_v2_switch_linked_profile(
#                 %s, %s, 
#                 NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
#             )
#             """, 
#             (requester_id, target_profile_id)
#         )
#         result = cur.fetchone()

#         if result['p_status_code'] == 200:
            
#             # 4. Generate Token matching exactly the login format
#             new_token = TokenGenerator.generate_profile_token(
#                 user_id=result['p_new_user_id'],
#                 email=result.get('p_email'),
#                 mobile=result.get('p_mobile'),
#                 name=result['p_full_name'],
#                 username=result['p_username'],
#                 role_id=result.get('p_role_id'),           
#                 roles=result.get('p_roles', []),
#                 sid=old_sid,                          # Carried over from old token
#                 sub_id=result['p_subscription_code']  # The active subscription ID
#             )
            
#             return api_response(
#                 message=result['p_message'], 
#                 code=200, 
#                 status="success",
#                 data={
#                     "token": new_token,
#                     "active_profile": {
#                         "user_id": result['p_new_user_id'],
#                         "username": result['p_username'],       
#                         "full_name": result['p_full_name'],     
#                         "profile_id": target_profile_id,
#                         "role": result['p_role_name'],
#                         "is_default": 1,
#                         "subscription_id": result['p_subscription_code'], 
#                         "plan": result['p_subscription_info']
#                     }
#                 }
#             )
        
#         return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()

# controllers/common/user_profile.py

def switch_profile():
    conn = None
    try:
        # 1. Grab old token payload to preserve "sid" (Session ID)
        old_token_payload = TokenVerifier.get_user_payload()
        old_sid = old_token_payload.get('sid') if old_token_payload else None

        # 2. Auth Check
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        requester_id = int(user_id_str)
        
        data = request.get_json() or {}
        target_profile_id = data.get('profile_id')

        if not target_profile_id: 
            return api_response(message="profile_id required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 3. Call SP (Expecting 13 OUT params -> 13 NULLs)
        cur.execute(
            """
            CALL login.usp_v2_switch_linked_profile(
                %s, %s, 
                NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
            )
            """, 
            (requester_id, target_profile_id)
        )
        result = cur.fetchone()

        if result['p_status_code'] == 200:
            
            # Extract basic data
            roles = result.get('p_roles', [])
            active_sub_id = result.get('p_subscription_code')
            role_id = result.get('p_role_id')

            # =========================================================
            # STRIP SUBSCRIPTION ID FROM ROLES 
            # =========================================================
            cleaned_roles = [{k: v for k, v in r.items() if k != 'subscription_id'} for r in roles]

            # Calculate Expiration
            import datetime
            exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)

            # =================================================================
            # TOKEN 1: MAIN AUTH TOKEN (No Sub ID)
            # =================================================================
            jwt_payload = {
                "sub": str(result['p_new_user_id']),
                "name": result['p_full_name'],
                "username": result['p_username'],
                "email": result.get('p_email'),
                "mobile": result.get('p_mobile'),
                "role_id": role_id,
                "roles": cleaned_roles,
                "sid": old_sid, 
                "exp": int(exp_time.timestamp()) 
            }
            import jwt
            from config import JWT_SECRET
            auth_token = jwt.encode(jwt_payload, JWT_SECRET, algorithm="HS256")
            
            # =================================================================
            # TOKEN 2: SEPARATE SUBSCRIPTION TOKEN
            # =================================================================
            sub_token = None
            if active_sub_id:
                sub_payload = {
                    "subscription_id": active_sub_id,
                    "exp": int(exp_time.timestamp())
                }
                sub_token = jwt.encode(sub_payload, JWT_SECRET, algorithm="HS256")

            # Formatted Expiry string for the JSON response body
            exp_str = exp_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
            user_response = jwt_payload.copy()
            user_response["exp"] = exp_str
            
            # Build the exact same response shape as the Login API
            final_response = {
                "auth_token": auth_token,
                "subscription_token": sub_token,
                "subscription_id": active_sub_id,
                "user": user_response,
                "active_profile": {
                    "user_id": result['p_new_user_id'],
                    "username": result['p_username'],       
                    "full_name": result['p_full_name'],     
                    "profile_id": target_profile_id,
                    "role": result['p_role_name'],
                    "is_default": 1,
                    "subscription_id": active_sub_id, 
                    "plan": result['p_subscription_info']
                }
            }

            return api_response(
                message=result['p_message'], 
                code=200, 
                status="success",
                data=final_response
            )
        
        return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()