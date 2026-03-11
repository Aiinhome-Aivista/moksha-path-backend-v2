  
import hashlib
import uuid
import datetime
import jwt
from flask import request
import psycopg2.extras
from utils.token_helper import TokenVerifier
from config import get_db_connection, JWT_SECRET
from utils.api_response import api_response
from utils.email_sender import send_otp_email
from utils.sms_sender import send_sms_otp

 

# =========================================================
# API 1: SEND OTP (v4)
# =========================================================
def send_ui_otp_v4():
    """ 
    POST /auth/v4/send-otp
    Checks if user exists. If yes -> Sends OTP. 
    If no -> Returns 200 Success with new_user: true (requests both email and phone).
    """
    conn = None
    try:
        data = request.get_json()
        auth_identifier = data.get('auth_identifier')
        email = data.get('email', '')
        mobile = data.get('mobile', '') or data.get('phone', '')

        if not auth_identifier:
            return api_response(message="auth_identifier is required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute(
            "CALL login.usp_v4_send_otpv1(%s, %s, %s, NULL::VARCHAR, NULL::VARCHAR, NULL::INTEGER, NULL::BOOLEAN)", 
            (auth_identifier, email, mobile)
        )
        result = cur.fetchone()

        if result['p_status_code'] == 200:
            otp_code = result['p_otp_code']
            is_new_user = result['p_is_new_user']

            # Only attempt to send emails/SMS if an OTP was actually generated
            if otp_code:
                # Send Email OTP if identifier contains '@' or explicit email passed
                if '@' in auth_identifier or email: 
                    send_otp_email(email or auth_identifier, otp_code)
                
                # Send SMS OTP if identifier is digits or explicit mobile passed
                if auth_identifier.replace('+','').isdigit() or mobile:
                    target_mobile = mobile or auth_identifier
                    if not target_mobile.startswith('+'): target_mobile = f"+91{target_mobile}"
                    send_sms_otp(target_mobile, otp_code)

            return api_response(
                message=result['p_message'], 
                code=200, 
                status="success", 
                data={"new_user": is_new_user}
            )
            
        return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: 
            cur.close()
            conn.close()


 
# =========================================================
# API 2: VERIFY OTP AND LOGIN/REGISTER (v4)
# =========================================================
# def verify_and_login_v4():
#     """ 
#     POST /auth/v4/verify-and-login
#     Validates OTP. 
#     - 1 Complete Profile -> Creates session & logs in.
#     - Multiple/Incomplete -> Skips session, returns records & temporary token with user details.
#     """
#     conn = None
#     try:
#         data = request.get_json()
#         auth_identifier = data.get('auth_identifier')
#         otp = data.get('otp')
#         email = data.get('email', '')
#         mobile = data.get('mobile', '') or data.get('phone', '')
        
#         ip_address = request.remote_addr
#         user_agent = request.headers.get('User-Agent', '')
        
#         random_str = str(uuid.uuid4())
#         refresh_token = hashlib.md5(random_str.encode()).hexdigest()

#         if not auth_identifier or not otp:
#             return api_response(message="auth_identifier and otp are required", code=400, status="error")

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
#         cur.execute(
#             """CALL login.usp_v4_verify_otp_and_loginv1(
#                 %s, %s, %s, %s, %s, %s, %s, 
#                 '{}'::jsonb, 0::integer, ''::varchar, 0::integer
#             )""", 
#             (auth_identifier, otp, email, mobile, ip_address, user_agent, refresh_token)
#         )
#         result = cur.fetchone()

#         if result['o_status_code'] == 200:
#             profiles = result['o_profiles_json']
#             session_id = result['o_session_id']

#             exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
#             exp_str = exp_time.strftime('%a, %d %b %Y %H:%M:%S GMT') 

#             if session_id:
#                 # SCENARIO A: 1 Complete Profile (Fully Logged In)
                
#                 # =======================================================================
#                 # SMART FIX: Grab the EXACT profile slot the database assigned this device
#                 # =======================================================================
#                 current_profile = next((p for p in profiles if p.get('current_user') is True), profiles[0])
                
#                 roles = current_profile.get('roles') or []
#                 active_sub_id = roles[0].get('subscription_id') if roles else None
#                 role_id = roles[0].get('role_id') if roles else None

#                 # =======================================================================
#                 # JWT FIX: Explicitly map email, mobile, and username here!
#                 # =======================================================================
#                 jwt_payload = {
#                     "sub": str(current_profile.get('sub')),
#                     "name": current_profile.get('name'),
#                     "username": current_profile.get('username'),
#                     "email": current_profile.get('email'),        # <--- ADDED
#                     "mobile": current_profile.get('mobile'),      # <--- ADDED
#                     "role_id": role_id,
#                     "roles": roles,
#                     "sid": str(session_id),
#                     "sub_id": active_sub_id,
#                     "exp": int(exp_time.timestamp()) 
#                 }
#                 token = jwt.encode(jwt_payload, JWT_SECRET, algorithm="HS256")

#                 user_response = jwt_payload.copy()
#                 user_response["exp"] = exp_str

#                 final_response = {
#                     "refresh_token": refresh_token,
#                     "subscription_id": active_sub_id,
#                     "token": token,
#                     "user": user_response
#                 }
#             else:
#                 # SCENARIO B: Multi-Profile OR Incomplete (Session Skipped)
#                 first_profile = profiles[0] if profiles else {}
#                 first_roles = first_profile.get('roles') or []
#                 first_role_id = first_roles[0].get('role_id') if first_roles else None
                
#                 # Also add them to the temporary setup token just in case your frontend needs them!
#                 account_payload = {
#                     "sub": str(first_profile.get('sub', '')),
#                     "email": first_profile.get('email'),
#                     "mobile": first_profile.get('mobile'),
#                     "username": first_profile.get('username'),
#                     "auth_identifier": auth_identifier,
#                     "role_id": first_role_id,
#                     "status": "profile_selection_required",
#                     "exp": int(exp_time.timestamp())
#                 }
#                 token = jwt.encode(account_payload, JWT_SECRET, algorithm="HS256")
                
#                 final_response = {
#                     "refresh_token": None,
#                     "subscription_id": None,
#                     "token": token,
#                     "user": None,          
#                     "profiles": profiles   
#                 }

#             return api_response(message=result['o_message'], code=200, data=final_response, status="success")
            
#         return api_response(message=result['o_message'], code=result['o_status_code'], status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: 
#             cur.close()
#             conn.close()
 

# def select_profile_v4():
#     """ 
#     POST /auth/v4/select-profile
#     User clicks a specific profile. Handles active sessions across multiple devices.
#     Body: { "user_id": 470, "subscription_id": "...", "force_login": true/false }
#     """
#     conn = None
#     try:
#         # =====================================================================
#         # 1. EXTRACT CURRENT USER AND SPECIFIC SESSION FROM JWT 
#         # =====================================================================
#         payload = TokenVerifier.get_user_payload()
#         current_user_id = payload.get('sub') if payload else None
#         current_session_id = payload.get('sid') if payload else None

#         # =====================================================================
#         # 2. PARSE INCOMING REQUEST FOR TARGET USER
#         # =====================================================================
#         data = request.get_json()
#         target_user_id = data.get('user_id')
#         subscription_id = data.get('subscription_id') 
#         force_login = data.get('force_login', False) 
        
#         if not target_user_id:
#             return api_response(message="user_id is required", code=400, status="error")

#         ip_address = request.remote_addr
#         user_agent = request.headers.get('User-Agent', '')
        
#         random_str = str(uuid.uuid4())
#         refresh_token = hashlib.md5(random_str.encode()).hexdigest()

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
#         # =====================================================================
#         # 3. PINPOINT LOGOUT FOR THE CURRENT USER (Call new SP)
#         # =====================================================================
#         # If they pass the token for 471, and want to log into 470, kill 471's session!
#         if current_session_id and current_user_id and str(current_user_id) != str(target_user_id):
#             cur.execute(
#                 "CALL login.usp_v4_logout_session(%s::integer, %s::bigint)",
#                 (current_session_id, current_user_id)
#             )

#         # =====================================================================
#         # 4. CALL SP TO LOGIN NEW TARGET USER 
#         # =====================================================================
#         cur.execute(
#             """CALL login.usp_v4_select_profile(
#                 %s::bigint, %s, %s, %s, %s, %s::boolean,
#                 ''::varchar, ''::varchar, ''::varchar, ''::varchar, '{}'::jsonb, 0::integer, ''::varchar, 0::integer
#             )""", 
#             (target_user_id, subscription_id, ip_address, user_agent, refresh_token, force_login)
#         )
#         result = cur.fetchone()

#         if result['o_status_code'] == 200:
#             session_id = result['o_session_id']
#             full_name = result['o_full_name']
#             username = result['o_username']
#             email = result['o_email']
#             mobile = result['o_phone']
#             roles = result['o_role_json']
            
#             active_sub_id = roles[0].get('subscription_id') if roles else subscription_id

#             exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
#             exp_str = exp_time.strftime('%a, %d %b %Y %H:%M:%S GMT')

#             # =================================================================
#             # 5. GENERATE BRAND NEW JWT FOR THE TARGET USER
#             # =================================================================
#             jwt_payload = {
#                 "sub": str(target_user_id),
#                 "email": email,             
#                 "mobile": mobile,           
#                 "name": full_name,
#                 "username": username,
#                 "role_id": roles[0].get('role_id') if roles else None,
#                 "roles": roles,
#                 "sid": str(session_id),
#                 "sub_id": active_sub_id,
#                 "exp": int(exp_time.timestamp()) 
#             }
#             token = jwt.encode(jwt_payload, JWT_SECRET, algorithm="HS256")
            
#             user_response = jwt_payload.copy()
#             user_response["exp"] = exp_str

#             final_response = {
#                 "refresh_token": refresh_token,
#                 "subscription_id": active_sub_id,
#                 "token": token,
#                 "user": user_response
#             }
#             return api_response(message=result['o_message'], code=200, data=final_response, status="success")

#         elif result['o_status_code'] == 409:
#             return api_response(
#                 message=result['o_message'], 
#                 code=200, 
#                 data={"requires_force_login": True}, 
#                 status="success"
#             )
            
#         return api_response(message=result['o_message'], code=result['o_status_code'], status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: 
#             cur.close()
#             conn.close()




# v1 code #




def verify_and_login_v4():
    """ 
    POST /auth/v4/verify-and-login
    Validates OTP. 
    - 1 Complete Profile -> Creates session & logs in, returns 2 distinct tokens.
    - Multiple/Incomplete -> Skips session, returns records & temporary auth token.
    """
    conn = None
    try:
        data = request.get_json()
        auth_identifier = data.get('auth_identifier')
        otp = data.get('otp')
        email = data.get('email', '')
        mobile = data.get('mobile', '') or data.get('phone', '')
        
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        random_str = str(uuid.uuid4())
        refresh_token = hashlib.md5(random_str.encode()).hexdigest()

        if not auth_identifier or not otp:
            return api_response(message="auth_identifier and otp are required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute(
            """CALL login.usp_verify_otp_and_loginv1(
                %s, %s, %s, %s, %s, %s, %s, 
                '{}'::jsonb, 0::integer, ''::varchar, 0::integer
            )""", 
            (auth_identifier, otp, email, mobile, ip_address, user_agent, refresh_token)
        )
        result = cur.fetchone()

        if result['o_status_code'] == 200:
            profiles = result['o_profiles_json']
            session_id = result['o_session_id']

            exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
            exp_str = exp_time.strftime('%a, %d %b %Y %H:%M:%S GMT') 

            if session_id:
                # =======================================================================
                # SCENARIO A: 1 Complete Profile (Fully Logged In)
                # =======================================================================
                current_profile = next((p for p in profiles if p.get('current_user') is True), profiles[0])
                
                roles = current_profile.get('roles') or []
                active_sub_id = roles[0].get('subscription_id') if roles else None
                role_id = roles[0].get('role_id') if roles else None

                # 1. AUTH PAYLOAD (Identity & Session Info)
                auth_payload = {
                    "sub": str(current_profile.get('sub')),
                    "name": current_profile.get('name'),
                    "username": current_profile.get('username'),
                    "email": current_profile.get('email'),        
                    "mobile": current_profile.get('mobile'),      
                    "sid": str(session_id),
                    "exp": int(exp_time.timestamp()) 
                }

                # 2. SUBSCRIPTION PAYLOAD (Context & Authorization Info)
                sub_payload = {
                    "sub": str(current_profile.get('sub')), # Link to user
                    "role_id": role_id,
                    "roles": roles,
                    "sub_id": active_sub_id,
                    "exp": int(exp_time.timestamp())
                }

                # Encode both tokens
                auth_token = jwt.encode(auth_payload, JWT_SECRET, algorithm="HS256")
                sub_token = jwt.encode(sub_payload, JWT_SECRET, algorithm="HS256")

                user_response = auth_payload.copy()
                user_response["exp"] = exp_str

                final_response = {
                    "refresh_token": refresh_token,
                    "subscription_id": active_sub_id,
                    "auth_token": auth_token,               # <-- Main bearer token
                    "subscription_token": sub_token,        # <-- Subscription header token
                    "user": user_response,
                    "subscription_data": sub_payload
                }
            else:
                # =======================================================================
                # SCENARIO B: Multi-Profile OR Incomplete (Session Skipped)
                # =======================================================================
                first_profile = profiles[0] if profiles else {}
                first_roles = first_profile.get('roles') or []
                first_role_id = first_roles[0].get('role_id') if first_roles else None
                user_id_str = str(first_profile.get('sub', ''))
                
                # Temporary setup token
                account_payload = {
                    # "sub": str(first_profile.get('sub', '')),
                    "sub": user_id_str,
                    "email": first_profile.get('email'),
                    "mobile": first_profile.get('mobile'),
                    "username": first_profile.get('username'),
                    "auth_identifier": auth_identifier,
                    "role_id": first_role_id,
                    "sid": user_id_str,
                    "status": "profile_selection_required",
                    "exp": int(exp_time.timestamp())
                }
                
                setup_token = jwt.encode(account_payload, JWT_SECRET, algorithm="HS256")
                
                final_response = {
                    "refresh_token": None,
                    "subscription_id": None,
                    "auth_token": setup_token,         # Temporary Auth Token
                    "subscription_token": None,        # No sub token until profile selected
                    "user": None,          
                    "profiles": profiles   
                }

            return api_response(message=result['o_message'], code=200, data=final_response, status="success")
            
        return api_response(message=result['o_message'], code=result['o_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: 
            cur.close()
            conn.close()





def select_profile_v4():
    """ 
    POST /auth/v4/select-profile
    User clicks a specific profile. Handles active sessions across multiple devices.
    Body: { "user_id": 470, "subscription_id": "...", "force_login": true/false }
    """
    conn = None
    try:
        # =====================================================================
        # 1. EXTRACT CURRENT USER AND SPECIFIC SESSION FROM JWT 
        # =====================================================================
        payload = TokenVerifier.get_user_payload()
        current_user_id = payload.get('sub') if payload else None
        current_session_id = payload.get('sid') if payload else None

        # =====================================================================
        # 2. PARSE INCOMING REQUEST FOR TARGET USER
        # =====================================================================
        data = request.get_json()
        target_user_id = data.get('user_id')
        subscription_id = data.get('subscription_id') 
        force_login = data.get('force_login', False) 
        
        if not target_user_id:
            return api_response(message="user_id is required", code=400, status="error")

        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        random_str = str(uuid.uuid4())
        refresh_token = hashlib.md5(random_str.encode()).hexdigest()

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # =====================================================================
        # 3. PINPOINT LOGOUT FOR THE CURRENT USER (Now performs DELETE)
        # =====================================================================
        # If they pass the token for 471, and want to log into 470, kill 471's session!
        if current_session_id and current_user_id and str(current_user_id) != str(target_user_id):
            cur.execute(
                "CALL login.usp_logout_session_v1(%s::integer, %s::bigint)",
                (current_session_id, current_user_id)
            )

        # =====================================================================
        # 4. CALL SP TO LOGIN NEW TARGET USER 
        # =====================================================================
        cur.execute(
            """CALL login.usp_select_profile_v1(
                %s::bigint, %s, %s, %s, %s, %s::boolean,
                ''::varchar, ''::varchar, ''::varchar, ''::varchar, '{}'::jsonb, 0::integer, ''::varchar, 0::integer
            )""", 
            (target_user_id, subscription_id, ip_address, user_agent, refresh_token, force_login)
        )
        result = cur.fetchone()

        if result['o_status_code'] == 200:
            session_id = result['o_session_id']
            full_name = result['o_full_name']
            username = result['o_username']
            email = result['o_email']
            mobile = result['o_phone']
            roles = result['o_role_json']
            
            active_sub_id = roles[0].get('subscription_id') if roles else subscription_id

            exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
            exp_str = exp_time.strftime('%a, %d %b %Y %H:%M:%S GMT')

            # =================================================================
            # 5. GENERATE TWO TOKENS FOR THE TARGET USER
            # =================================================================
            
            # --- AUTH TOKEN PAYLOAD ---
            auth_payload = {
                "sub": str(target_user_id),
                "name": full_name,
                "username": username,
                "email": email,            
                "mobile": mobile,          
                "sid": str(session_id),
                "exp": int(exp_time.timestamp()) 
            }
            
            # --- SUBSCRIPTION TOKEN PAYLOAD ---
            sub_payload = {
                "sub": str(target_user_id),
                "role_id": roles[0].get('role_id') if roles else None,
                "roles": roles,
                "sub_id": active_sub_id,
                "exp": int(exp_time.timestamp())
            }

            auth_token = jwt.encode(auth_payload, JWT_SECRET, algorithm="HS256")
            sub_token = jwt.encode(sub_payload, JWT_SECRET, algorithm="HS256")
            
            user_response = auth_payload.copy()
            user_response["exp"] = exp_str

            final_response = {
                "auth_token": auth_token,
                "refresh_token": refresh_token,
                "subscription_data": sub_payload,
                "subscription_id": active_sub_id,
                "subscription_token": sub_token,
                "user": user_response
            }
            return api_response(message=result['o_message'], code=200, data=final_response, status="success")

        elif result['o_status_code'] == 409:
            return api_response(
                message=result['o_message'], 
                code=200, 
                data={"requires_force_login": True}, 
                status="success"
            )
            
        return api_response(message=result['o_message'], code=result['o_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: 
            cur.close()
            conn.close()




