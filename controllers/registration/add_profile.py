import hashlib
import uuid
import datetime
import jwt
from flask import request
import psycopg2.extras

from config import get_db_connection, JWT_SECRET
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription 

# =========================================================
# API 4: ADD PROFILE (v4)
# =========================================================
# def add_profile_v4():
#     """ 
#     POST /auth/v4/add-profile
#     Decodes temporary JWT to get email/mobile securely.
#     Updates the shell user (or adds a new profile) and creates an active session.
#     Body: { "actual_name": "...", "profile_name": "...", "role_id": 1 }
#     Headers: Authorization: Bearer <temporary_token>
#     """
#     conn = None
#     try:
#         # 1. Securely Extract Token from Headers
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith("Bearer "):
#             return api_response(message="Missing or invalid Authorization header", code=401, status="error")
        
#         token_string = auth_header.split(" ")[1]
        
#         # 2. Decode Token to get Email and Mobile
#         try:
#             decoded_token = jwt.decode(token_string, JWT_SECRET, algorithms=["HS256"])
#         except jwt.ExpiredSignatureError:
#             return api_response(message="Session expired. Please verify OTP again.", code=401, status="error")
#         except jwt.InvalidTokenError:
#             return api_response(message="Invalid authorization token.", code=401, status="error")
            
#         email = decoded_token.get('email')
#         mobile = decoded_token.get('mobile')
        
#         if not email and not mobile:
#             return api_response(message="Token payload is missing account identifiers.", code=400, status="error")

#         # 3. Extract UI Payload Data
#         data = request.get_json()
#         actual_name = data.get('actual_name')
#         profile_name = data.get('profile_name')
#         role_id = data.get('role_id')
        
#         if not actual_name or not profile_name or not role_id:
#             return api_response(message="actual_name, profile_name, and role_id are required", code=400, status="error")

#         ip_address = request.remote_addr
#         user_agent = request.headers.get('User-Agent', '')
        
#         random_str = str(uuid.uuid4())
#         refresh_token = hashlib.md5(random_str.encode()).hexdigest()

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
#         # 4. Call Stored Procedure
#         cur.execute(
#             """CALL login.usp_v4_add_profile(
#                 %s, %s, %s, %s, %s, %s, %s, %s, 
#                 0::bigint, '{}'::jsonb, 0::integer, ''::varchar, 0::integer
#             )""", 
#             (email, mobile, actual_name, profile_name, role_id, ip_address, user_agent, refresh_token)
#         )
#         result = cur.fetchone()

#         # =======================================================
#         # 5. HANDLE RESPONSES
#         # =======================================================
#         if result['o_status_code'] == 200:
#             user_id = result['o_user_id']
#             roles = result['o_role_json'] or []
#             session_id = result['o_session_id']
            
#             active_sub_id = get_active_subscription(user_id)
            
#             if roles:
#                 roles[0]['subscription_id'] = active_sub_id

#             exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
#             exp_str = exp_time.strftime('%a, %d %b %Y %H:%M:%S GMT') 

#             # ---> UPDATED: Now packing email and mobile into the final token! <---
#             jwt_payload = {
#                 "sub": str(user_id), 
#                 "email": email,
#                 "mobile": mobile,
#                 "name": actual_name, 
#                 "username": profile_name,
#                 "roles": roles, 
#                 "sid": str(session_id), 
#                 "sub_id": active_sub_id,
#                 "exp": int(exp_time.timestamp()) 
#             }
#             new_access_token = jwt.encode(jwt_payload, JWT_SECRET, algorithm="HS256")
            
#             user_response = jwt_payload.copy()
#             user_response["exp"] = exp_str

#             final_response = {
#                 "refresh_token": refresh_token,
#                 "subscription_id": active_sub_id,
#                 "token": new_access_token,
#                 "user": user_response
#             }
#             return api_response(message=result['o_message'], code=200, data=final_response, status="success")
            
#         elif result['o_status_code'] == 409:
#             return api_response(message=result['o_message'], code=200, data=None, status="success")

#         return api_response(message=result['o_message'], code=result['o_status_code'], status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: 
#             cur.close()
#             conn.close()



# =========================================================
# API 4: ADD PROFILE (v4)
# =========================================================
def add_profile_v4():
    """ 
    POST /auth/v4/add-profile
    Adds a new profile (Student or Parent) and maps board/class if provided.
    Headers: Authorization: Bearer <temporary_token>
    """
    conn = None
    try:
        # 1. Securely Extract Token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return api_response(message="Missing or invalid Authorization header", code=401, status="error")
        
        token_string = auth_header.split(" ")[1]
        
        try:
            decoded_token = jwt.decode(token_string, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return api_response(message="Session expired. Please verify OTP again.", code=401, status="error")
        except jwt.InvalidTokenError:
            return api_response(message="Invalid authorization token.", code=401, status="error")
            
        email = decoded_token.get('email')
        mobile = decoded_token.get('mobile')
        
        if not email and not mobile:
            return api_response(message="Token payload is missing account identifiers.", code=400, status="error")

        # 2. Extract UI Payload Data
        data = request.get_json()
        actual_name = data.get('actual_name')
        profile_name = data.get('profile_name')
        role_id = data.get('role_id')
        
        # Optional Academic fields for Students
        board_id = data.get('board_id')
        class_id = data.get('class_id')
        institute_id = data.get('institute_id')
        subscription_id = data.get('subscription_id') # Can be null for new users
        
        if not actual_name or not profile_name or not role_id:
            return api_response(message="actual_name, profile_name, and role_id are required", code=400, status="error")

        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        random_str = str(uuid.uuid4())
        refresh_token = hashlib.md5(random_str.encode()).hexdigest()

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # 3. Call Stored Procedure
        cur.execute(
            """CALL login.usp_v4_add_profile_withboard_details(
                %s, %s, %s, %s, %s, %s::integer, %s::integer, %s::integer, %s::varchar, %s, %s, %s, 
                0::bigint, '{}'::jsonb, 0::integer, ''::varchar, 0::integer
            )""", 
            (email, mobile, actual_name, profile_name, role_id, board_id, class_id, institute_id, subscription_id, ip_address, user_agent, refresh_token)
        )
        result = cur.fetchone()

        if result['o_status_code'] == 200:
            user_id = result['o_user_id']
            roles = result['o_role_json'] or []
            session_id = result['o_session_id']
            
            # Use helper to get active subscription (overriding if null)
            active_sub_id = get_active_subscription(user_id)
            if roles:
                roles[0]['subscription_id'] = active_sub_id

            exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
            exp_str = exp_time.strftime('%a, %d %b %Y %H:%M:%S GMT') 

            role_id_value = roles[0].get('role_id') if roles else None
            jwt_payload = {
                "sub": str(user_id), "email": email, "mobile": mobile,
                "name": actual_name, "username": profile_name,
                "role_id": role_id_value,
                "roles": roles, 
                "sid": str(session_id), "sub_id": active_sub_id, "exp": int(exp_time.timestamp()) 
            }
            new_access_token = jwt.encode(jwt_payload, JWT_SECRET, algorithm="HS256")
            
            user_response = jwt_payload.copy()
            user_response["exp"] = exp_str

            final_response = {
                "refresh_token": refresh_token,
                "subscription_id": active_sub_id,
                "token": new_access_token,
                "user": user_response
            }
            return api_response(message=result['o_message'], code=200, data=final_response, status="success")
            
        elif result['o_status_code'] == 409:
            return api_response(message=result['o_message'], code=200, data=None, status="success")

        return api_response(message=result['o_message'], code=result['o_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: 
            cur.close()
            conn.close()