# # import jwt
# # import datetime
# # import uuid
# # from flask import request
# # from config import get_db_connection, JWT_SECRET
# # from utils.api_response import api_response
# # from utils.email_sender import send_otp_email
# # from utils.sms_sender import send_sms_otp
# # from utils.username_generator import generate_username_suggestions
# # # =========================================================
# # # STEP 1: SEND OTP (Email OR Mobile)
# # # =========================================================
# # def send_ui_otp():
# #     """ 
# #     POST /auth/send-otp 
# #     Body: { "username": "...", "email": "..." } OR { "username": "...", "phone": "..." }
# #     """
# #     conn = None
# #     try:
# #         data = request.get_json()
# #         username = data.get('username')
# #         email = data.get('email')
        
# #         # Accept 'mobile' or 'phone' key for flexibility
# #         mobile = data.get('mobile')
# #         if not mobile: 
# #             mobile = data.get('phone')

# #         # Validation
# #         if not username:
# #             return api_response(message="Username is required", code=400, status="error")
# #         if not email and not mobile:
# #              return api_response(message="Email or Phone is required", code=400, status="error")

# #         conn = get_db_connection()
# #         conn.autocommit = True
# #         cur = conn.cursor()
        
# #         # Call Stored Procedure
# #         # Logic: Upserts user, generates OTP, saves to 'otp_code' (if email) or 'phone_otp' (if mobile)
# #         cur.execute(
# #             "CALL sp_ui_send_otp_mobile_email_final(%s, %s, %s, NULL::VARCHAR, NULL::VARCHAR, NULL::INTEGER)", 
# #             (username, email, mobile)
# #         )
# #         result = cur.fetchone()

# #         if result['p_status_code'] == 200:
# #             otp_code = result['p_otp_code']
            
# #             # Send Email OTP
# #             if email: 
# #                 send_otp_email(email, otp_code)
            
# #             # Send SMS OTP
# #             if mobile:
# #                 # Ensure country code (default to +91 if missing)
# #                 if not mobile.startswith('+'): 
# #                     mobile = f"+91{mobile}"
                
# #                 sms_result = send_sms_otp(mobile, otp_code)
# #                 # Optional: Log SMS failure but don't crash flow if needed
# #                 if not sms_result.get("success"):
# #                      print(f"SMS Failed: {sms_result.get('message')}")

# #             return api_response(message=result['p_message'], code=200)
            
# #         return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

# #     except Exception as e:
# #         return api_response(message=str(e), code=500, status="error")
# #     finally:
# #         if conn: conn.close()


# # # =========================================================
# # # STEP 2: VERIFY OTP (Specific Contact + OTP)
# # # =========================================================
# # def verify_ui_otp():
# #     """ 
# #     POST /auth/verify-otp 
# #     Body: { "username": "...", "email": "...", "otp": "..." } 
# #     OR    { "username": "...", "phone": "...", "otp": "..." }
# #     """
# #     conn = None
# #     try:
# #         data = request.get_json()
# #         username = data.get('username')
# #         otp = data.get('otp')
# #         email = data.get('email')
        
# #         mobile = data.get('mobile')
# #         if not mobile: 
# #             mobile = data.get('phone') 

# #         # Validation
# #         if not username or not otp: 
# #             return api_response(message="Username and OTP are required", code=400, status="error")
        
# #         if not email and not mobile:
# #             return api_response(message="Must provide Email or Phone to verify", code=400, status="error")

# #         conn = get_db_connection()
# #         conn.autocommit = True
# #         cur = conn.cursor()
        
# #         # Call Stored Procedure
# #         # Logic: Checks 'otp_code' if email provided, or 'phone_otp' if mobile provided
# #         cur.execute(
# #             "CALL sp_ui_verify_otp_mobile_email_final(%s, %s, %s, %s, NULL::VARCHAR, NULL::INTEGER)", 
# #             (username, email, mobile, otp)
# #         )
# #         result = cur.fetchone()

# #         if result['p_status_code'] == 200:
# #             return api_response(message="Verified Successfully", code=200)
            
# #         return api_response(message=result['p_message'], code=400, status="error")

# #     except Exception as e:
# #         return api_response(message=str(e), code=500, status="error")
# #     finally:
# #         if conn: conn.close()


# # # =========================================================
# # # STEP 3: FINAL REGISTRATION / SIGN IN
# # # =========================================================
# # def complete_ui_signup():
# #     """ 
# #     POST /auth/register 
# #     Body: { "role_id": 4, "username": "...", "full_name": "...", "email": "...", "mobile": "..." }
# #     """
# #     conn = None
# #     try:
# #         data = request.get_json()
        
# #         # Extract inputs
# #         role_id = data.get('role_id')
# #         username = data.get('username')
# #         full_name = data.get('full_name')
# #         email = data.get('email')
        
# #         mobile = data.get('mobile')
# #         if not mobile: 
# #             mobile = data.get('phone')

# #         # Validation
# #         if not role_id or not username: 
# #             return api_response(message="Role ID and Username required", code=400, status="error")

# #         conn = get_db_connection()
# #         conn.autocommit = True
# #         cur = conn.cursor()
        
# #         # Session Data
# #         refresh_token = str(uuid.uuid4())
# #         ip = request.remote_addr
# #         agent = request.headers.get('User-Agent')

# #         # Call Stored Procedure (Using the name from your error logs)
# #         cur.execute("""
# #             CALL sp_ui_complete_signup_mobile_email_final(
# #                 %s, %s, %s, %s, %s, %s, %s, %s, 
# #                 NULL::INTEGER, NULL::VARCHAR, NULL::JSONB, NULL::INTEGER, NULL::VARCHAR, NULL::INTEGER
# #             )
# #             """, 
# #             (role_id, username, full_name, email, mobile, ip, agent, refresh_token)
# #         )
# #         result = cur.fetchone()

# #         if result['p_status_code'] == 200:
# #             # Create JWT Payload
# #             payload = {
# #                 "sub": str(result['p_user_id']),
# #                 "name": result['p_full_name_out'],
# #                 "username": username,
# #                 "roles": result['p_role_json'],
# #                 "sid": str(result['p_session_id']),
# #                 "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
# #             }
# #             token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
            
# #             return api_response(message="Login Successful", code=200, data={
# #                 "token": token,
# #                 "refresh_token": refresh_token,
# #                 "user": payload
# #             })
        
# #         return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

# #     except Exception as e:
# #         return api_response(message=str(e), code=500, status="error")
# #     finally:
# #         if conn: conn.close()





# # # 1. GET SUGGESTIONS (Call when user types Name)
# # def get_username_suggestions():
# #     try:
# #         # 1. Get the name directly from the URL input
# #         full_name = request.args.get('name') 
        
# #         if not full_name: 
# #             return api_response(message="Name required", code=400, status="error")
             
# #         # 2. Generate and check availability (No user ID needed)
# #         suggestions = generate_username_suggestions(full_name)
        
# #         return api_response(message="Suggestions fetched", code=200, data={"suggestions": suggestions})
# #     except Exception as e:
# #         return api_response(message=str(e), code=500, status="error")
    

# # # 2. CHECK CUSTOM USERNAME (Call when user types custom username)
# # def check_username_availability():
# #     conn = None
# #     try:
# #         data = request.get_json()
# #         username = data.get('username')
# #         if not username: return api_response(message="Username required", code=400, status="error")

# #         conn = get_db_connection()
# #         conn.autocommit = True
# #         cur = conn.cursor()
        
# #         cur.execute("CALL sp_check_username_availability(%s, NULL::BOOLEAN, NULL::VARCHAR, NULL::INTEGER)", (username,))
# #         result = cur.fetchone()
        
# #         return api_response(message=result['p_message'], code=result['p_status_code'], data={"available": result['p_is_available']})
# #     except Exception as e:
# #         return api_response(message=str(e), code=500, status="error")
# #     finally:
# #         if conn: conn.close()


# import hashlib
# import time

# import jwt
# import datetime
# import uuid
# from flask import request
# import psycopg2
# from config import get_db_connection, JWT_SECRET
# from utils.api_response import api_response
# from utils.email_sender import send_otp_email
# from utils.sms_sender import send_sms_otp
# from utils.username_generator import generate_username_suggestions
# # =========================================================
# # STEP 1: SEND OTP (Email OR Mobile)
# # =========================================================
# def send_ui_otp():
#     """ 
#     POST /auth/send-otp 
#     Body: { "username": "...", "email": "..." } OR { "username": "...", "phone": "..." }
#     """
#     conn = None
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         email = data.get('email')
        
#         # Accept 'mobile' or 'phone' key for flexibility
#         mobile = data.get('mobile')
#         if not mobile: 
#             mobile = data.get('phone')

#         # Validation
#         if not username:
#             return api_response(message="Username is required", code=400, status="error")
#         if not email and not mobile:
#              return api_response(message="Email or Phone is required", code=400, status="error")

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor()
        
#         # Call Stored Procedure
#         # Logic: Upserts user, generates OTP, saves to 'otp_code' (if email) or 'phone_otp' (if mobile)
#         cur.execute(
#             "CALL login.usp_v1_send_otp_mobile_email_final(%s, %s, %s, NULL::VARCHAR, NULL::VARCHAR, NULL::INTEGER)", 
#             (username, email, mobile)
#         )
#         result = cur.fetchone()

#         if result['p_status_code'] == 200:
#             otp_code = result['p_otp_code']
            
#             # Send Email OTP
#             if email: 
#                 send_otp_email(email, otp_code)
            
#             # Send SMS OTP
#             if mobile:
#                 # Ensure country code (default to +91 if missing)
#                 if not mobile.startswith('+'): 
#                     mobile = f"+91{mobile}"
                
#                 sms_result = send_sms_otp(mobile, otp_code)
#                 # Optional: Log SMS failure but don't crash flow if needed
#                 if not sms_result.get("success"):
#                      print(f"SMS Failed: {sms_result.get('message')}")

#             return api_response(message=result['p_message'], code=200)
            
#         return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()


# # =========================================================
# # STEP 2: VERIFY OTP (Specific Contact + OTP)
# # =========================================================
# def verify_ui_otp():
#     """ 
#     POST /auth/verify-otp 
#     Body: { "username": "...", "email": "...", "otp": "..." } 
#     OR    { "username": "...", "phone": "...", "otp": "..." }
#     """
#     conn = None
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         otp = data.get('otp')
#         email = data.get('email')
        
#         mobile = data.get('mobile')
#         if not mobile: 
#             mobile = data.get('phone') 

#         # Validation
#         if not username or not otp: 
#             return api_response(message="Username and OTP are required", code=400, status="error")
        
#         if not email and not mobile:
#             return api_response(message="Must provide Email or Phone to verify", code=400, status="error")

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor()
        
#         # Call Stored Procedure
#         # Logic: Checks 'otp_code' if email provided, or 'phone_otp' if mobile provided
#         cur.execute(
#             "CALL login.usp_v1_verify_otp_mobile_email_final(%s, %s, %s, %s, NULL::VARCHAR, NULL::INTEGER)", 
#             (username, email, mobile, otp)
#         )
#         result = cur.fetchone()

#         if result['p_status_code'] == 200:
#             return api_response(message="Verified Successfully", code=200)
            
#         return api_response(message=result['p_message'], code=400, status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()


# # =========================================================
# # STEP 3: FINAL REGISTRATION / SIGN IN
# # =========================================================
# # def complete_ui_signup():
# #     """ 
# #     POST /auth/register 
# #     Body: { "role_id": 4, "username": "...", "full_name": "...", "email": "...", "mobile": "..." }
# #     """
# #     conn = None
# #     try:
# #         data = request.get_json()
        
# #         # Extract inputs
# #         role_id = data.get('role_id')
# #         username = data.get('username')
# #         full_name = data.get('full_name')
# #         email = data.get('email')
        
# #         mobile = data.get('mobile')
# #         if not mobile: 
# #             mobile = data.get('phone')

# #         # Validation
# #         if not role_id or not username: 
# #             return api_response(message="Role ID and Username required", code=400, status="error")

# #         conn = get_db_connection()
# #         conn.autocommit = True
# #         cur = conn.cursor()
        
# #         # Session Data
# #         refresh_token = str(uuid.uuid4())
# #         ip = request.remote_addr
# #         agent = request.headers.get('User-Agent')

# #         # Call Stored Procedure (Using the name from your error logs)
# #         cur.execute("""
# #             CALL login.usp_v2_complete_signup_mobile_email_final(
# #                 %s, %s, %s, %s, %s, %s, %s, %s, 
# #                 NULL::INTEGER, NULL::VARCHAR, NULL::JSONB, NULL::INTEGER, NULL::VARCHAR, NULL::INTEGER
# #             )
# #             """, 
# #             (role_id, username, full_name, email, mobile, ip, agent, refresh_token)
# #         )
# #         result = cur.fetchone()

# #         if result['p_status_code'] == 200:
# #             # Create JWT Payload
# #             payload = {
# #                 "sub": str(result['p_user_id']),
# #                 "name": result['p_full_name_out'],
# #                 "username": username,
# #                 "roles": result['p_role_json'],
# #                 "sid": str(result['p_session_id']),
# #                 "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
# #             }
# #             token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
            
# #             return api_response(message="Login Successful", code=200, data={
# #                 "token": token,
# #                 "refresh_token": refresh_token,
# #                 "user": payload
# #             })
        
# #         return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

# #     except Exception as e:
# #         return api_response(message=str(e), code=500, status="error")
# #     finally:
# #         if conn: conn.close()



 
  

# def complete_ui_signup():
#     """ 
#     POST /auth/register 
#     Body: { "role_id": 4, "username": "...", "full_name": "...", "email": "...", "mobile": "..." }
#     """
#     conn = None
#     try:
#         data = request.get_json()
        
#         # Extract inputs
#         role_id = data.get('role_id')
#         username = data.get('username')
#         full_name = data.get('full_name')
        
#         # Safely extract and convert empty strings to None
#         email = data.get('email', '').strip() or None
#         mobile = data.get('mobile', '').strip() or data.get('phone', '').strip() or None

#         # Validation
#         if not role_id or not username: 
#             return api_response(message="Role ID and Username required", code=400, status="error")
#         if not email and not mobile:
#             return api_response(message="Please provide either an email or a mobile number", code=400, status="error")

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # <-- Required for dict-like column access
        
#         # Session Data (Hashing the refresh token to match your updated security logic)
#         random_str = str(uuid.uuid4())
#         refresh_token = hashlib.md5(random_str.encode()).hexdigest()
        
#         ip = request.remote_addr
#         agent = request.headers.get('User-Agent', 'Unknown')

#         # Call Stored Procedure
#         cur.execute("""
#             CALL login.usp_v2_complete_signup_mobile_email_final(
#                 %s, %s, %s, %s, %s, %s, %s, %s, 
#                 NULL::INTEGER, NULL::VARCHAR, NULL::JSONB, NULL::INTEGER, NULL::VARCHAR, NULL::INTEGER
#             )
#             """, 
#             (role_id, username, full_name, email, mobile, ip, agent, refresh_token)
#         )
#         result = cur.fetchone()

#         if result['p_status_code'] == 200:
            
#             # 1. Calculate Expiration Time (12 hours from now)
#             exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
            
#             # Format the time exactly as requested: "Wed, 25 Feb 2026 20:15:20 GMT"
#             exp_str = exp_time.strftime('%a, %d %b %Y %H:%M:%S GMT')

#             # 2. Build the exact User dictionary you requested
#             user_data = {
#                 "exp": exp_str,
#                 "name": result['p_full_name_out'],
#                 "roles": result['p_role_json'] or [],
#                 "sid": str(result['p_session_id']),
#                 "sub": str(result['p_user_id']),
#                 "username": username
#             }

#             # 3. Create the JWT Token 
#             # (Standard JWT requires 'exp' to be an integer timestamp inside the actual token)
#             token_payload = user_data.copy()
#             token_payload["exp"] = int(exp_time.timestamp()) 
#             token = jwt.encode(token_payload, JWT_SECRET, algorithm="HS256")
            
#             # 4. Final formatted output
#             final_data = {
#                 "token": token,
#                 "refresh_token": refresh_token,
#                 "user": user_data
#             }
            
#             return api_response(message=result['p_message'], code=200, data=final_data, status="success")
        
#         return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: 
#             cur.close()
#             conn.close()


# # 1. GET SUGGESTIONS (Call when user types Name)
# def get_username_suggestions():
#     try:
#         # 1. Get the name directly from the URL input
#         full_name = request.args.get('name') 
        
#         if not full_name: 
#             return api_response(message="Name required", code=400, status="error")
             
#         # 2. Generate and check availability (No user ID needed)
#         suggestions = generate_username_suggestions(full_name)
        
#         return api_response(message="Suggestions fetched", code=200, data={"suggestions": suggestions})
#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
    

# # 2. CHECK CUSTOM USERNAME (Call when user types custom username)
# def check_username_availability():
#     conn = None
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         if not username: return api_response(message="Username required", code=400, status="error")

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor()
        
#         cur.execute("CALL login.sp_check_username_availability(%s, NULL::BOOLEAN, NULL::VARCHAR, NULL::INTEGER)", (username,))
#         result = cur.fetchone()
        
#         return api_response(message=result['p_message'], code=result['p_status_code'], data={"available": result['p_is_available']})
#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()


import hashlib
import time
import jwt
import datetime
import uuid
from flask import request
import psycopg2
import psycopg2.extras  # FIX 1: Explicitly import extras!

from config import get_db_connection, JWT_SECRET
from utils.api_response import api_response
from utils.email_sender import send_otp_email
from utils.sms_sender import send_sms_otp
from utils.username_generator import generate_username_suggestions

# =========================================================
# STEP 1: SEND OTP (Email OR Mobile)
# =========================================================
def send_ui_otp():
    """ 
    POST /auth/send-otp 
    Body: { "username": "...", "email": "..." } OR { "username": "...", "phone": "..." }
    """
    conn = None
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        
        # Accept 'mobile' or 'phone' key for flexibility
        mobile = data.get('mobile')
        if not mobile: 
            mobile = data.get('phone')

        # Validation
        if not username:
            return api_response(message="Username is required", code=400, status="error")
        if not email and not mobile:
             return api_response(message="Email or Phone is required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        
        # FIX 2: Use RealDictCursor so result['p_status_code'] works
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute(
            "CALL login.usp_v1_send_otp_mobile_email_final(%s, %s, %s, NULL::VARCHAR, NULL::VARCHAR, NULL::INTEGER)", 
            (username, email, mobile)
        )
        result = cur.fetchone()

        if result['p_status_code'] == 200:
            otp_code = result['p_otp_code']
            
            # Send Email OTP
            if email: 
                send_otp_email(email, otp_code)
            
            # Send SMS OTP
            if mobile:
                if not mobile.startswith('+'): 
                    mobile = f"+91{mobile}"
                
                sms_result = send_sms_otp(mobile, otp_code)
                if not sms_result.get("success"):
                     print(f"SMS Failed: {sms_result.get('message')}")

            return api_response(message=result['p_message'], code=200)
            
        return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()


# =========================================================
# STEP 2: VERIFY OTP (Specific Contact + OTP)
# =========================================================
def verify_ui_otp():
    """ 
    POST /auth/verify-otp 
    Body: { "username": "...", "email": "...", "otp": "..." } 
    OR    { "username": "...", "phone": "...", "otp": "..." }
    """
    conn = None
    try:
        data = request.get_json()
        username = data.get('username')
        otp = data.get('otp')
        email = data.get('email')
        
        mobile = data.get('mobile')
        if not mobile: 
            mobile = data.get('phone') 

        # Validation
        if not username or not otp: 
            return api_response(message="Username and OTP are required", code=400, status="error")
        
        if not email and not mobile:
            return api_response(message="Must provide Email or Phone to verify", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        
        # FIX 2: Use RealDictCursor
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute(
            "CALL login.usp_v1_verify_otp_mobile_email_final(%s, %s, %s, %s, NULL::VARCHAR, NULL::INTEGER)", 
            (username, email, mobile, otp)
        )
        result = cur.fetchone()

        if result['p_status_code'] == 200:
            return api_response(message="Verified Successfully", code=200)
            
        return api_response(message=result['p_message'], code=400, status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()


# =========================================================
# STEP 3: FINAL REGISTRATION / SIGN IN
# =========================================================
def complete_ui_signup():
    """ 
    POST /auth/register 
    Body: { "role_id": 4, "username": "...", "full_name": "...", "email": "...", "mobile": "..." }
    """
    conn = None
    try:
        data = request.get_json()
        
        role_id = data.get('role_id')
        username = data.get('username')
        full_name = data.get('full_name')
        
        email = data.get('email', '').strip() or None
        mobile = data.get('mobile', '').strip() or data.get('phone', '').strip() or None

        if not role_id or not username: 
            return api_response(message="Role ID and Username required", code=400, status="error")
        if not email and not mobile:
            return api_response(message="Please provide either an email or a mobile number", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        random_str = str(uuid.uuid4())
        refresh_token = hashlib.md5(random_str.encode()).hexdigest()
        
        ip = request.remote_addr
        agent = request.headers.get('User-Agent', 'Unknown')

        cur.execute("""
            CALL login.usp_v2_complete_signup_mobile_email_final(
                %s, %s, %s, %s, %s, %s, %s, %s, 
                NULL::INTEGER, NULL::VARCHAR, NULL::JSONB, NULL::INTEGER, NULL::VARCHAR, NULL::INTEGER
            )
            """, 
            (role_id, username, full_name, email, mobile, ip, agent, refresh_token)
        )
        result = cur.fetchone()

        if result['p_status_code'] == 200:
            
            exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
            exp_str = exp_time.strftime('%a, %d %b %Y %H:%M:%S GMT')

            user_data = {
                "exp": exp_str,
                "name": result['p_full_name_out'],
                "roles": result['p_role_json'] or [],
                "sid": str(result['p_session_id']),
                "sub": str(result['p_user_id']),
                "username": username
            }

            token_payload = user_data.copy()
            token_payload["exp"] = int(exp_time.timestamp()) 
            token = jwt.encode(token_payload, JWT_SECRET, algorithm="HS256")
            
            final_data = {
                "token": token,
                "subscription_token": None,
                "refresh_token": refresh_token,
                "user": user_data
            }
            
            return api_response(message=result['p_message'], code=200, data=final_data, status="success")
        
        return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        # FIX 3: Removed unsafe cur.close() to prevent UnboundLocalError
        if conn: 
            conn.close()


# =========================================================
# HELPER: GET SUGGESTIONS
# =========================================================
def get_username_suggestions():
    try:
        full_name = request.args.get('name') 
        
        if not full_name: 
            return api_response(message="Name required", code=400, status="error")
             
        suggestions = generate_username_suggestions(full_name)
        
        return api_response(message="Suggestions fetched", code=200, data={"suggestions": suggestions})
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    

# =========================================================
# HELPER: CHECK CUSTOM USERNAME
# =========================================================
def check_username_availability():
    conn = None
    try:
        data = request.get_json()
        username = data.get('username')
        if not username: return api_response(message="Username required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        
        # FIX 2: Use RealDictCursor
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("CALL login.sp_check_username_availability(%s, NULL::BOOLEAN, NULL::VARCHAR, NULL::INTEGER)", (username,))
        result = cur.fetchone()
        
        return api_response(message=result['p_message'], code=result['p_status_code'], data={"available": result['p_is_available']})
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()