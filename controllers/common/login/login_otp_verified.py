import jwt
import datetime
import uuid
import hashlib
from flask import request
from config import get_db_connection, JWT_SECRET
from utils.api_response import api_response
from utils.email_sender import send_otp_email
from utils.sms_sender import send_sms_otp
import psycopg2.extras

# =========================================================
# STEP 1: SEND OTP
# =========================================================
def login_send_ui_otp():
    """ POST /api/v1/auth/send-otp """
    conn = None
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        mobile = data.get('mobile') or data.get('phone')

        if not username: 
            return api_response(message="Username is required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor()
        
        # Calls: usp_v1_send_otp_mobile_email_final (7 Args: username, email, phone, otp_out, message_out, status_out)
        # Note: In the SQL above, I removed the 'is_new_user' flag to simplify since this is strictly Login Flow.
        # But if your DB still expects 7 args, adjust accordingly. 
        # Based on my updated SQL above, it has 6 arguments.
        cur.execute(
            "CALL login.usp_v1_login_send_otp_mobile_email_final(%s, %s, %s, NULL::VARCHAR, NULL::VARCHAR, NULL::INTEGER)", 
            (username, email, mobile)
        )
        result = cur.fetchone()

        if result['p_status_code'] == 200:
            otp_code = result['p_otp_code']
            if email: send_otp_email(email, otp_code)
            if mobile: 
                if not mobile.startswith('+'): mobile = f"+91{mobile}"
                send_sms_otp(mobile, otp_code)

            return api_response(message=result['p_message'], code=200)
            
        return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()


# =========================================================
# STEP 2: VERIFY OTP
# =========================================================
def login_verify_ui_otp():
    """ POST /api/v1/auth/verify-otp """
    conn = None
    try:
        data = request.get_json()
        username = data.get('username')
        otp = data.get('otp')
        email = data.get('email')
        mobile = data.get('mobile') or data.get('phone')

        if not username or not otp: 
            return api_response(message="Username and OTP required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor()
        
        # Calls: usp_v1_verify_otp_mobile_email_final
        cur.execute(
            "CALL login.usp_v1_login_verify_otp_mobile_email_final(%s, %s, %s, %s, NULL::VARCHAR, NULL::INTEGER)", 
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
# STEP 3: LOGIN (Generates MD5 Token)
# =========================================================
# def login_login_user():
#     """ POST /api/v1/auth/login """
#     conn = None
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         email = data.get('email')
#         mobile = data.get('mobile') or data.get('phone')

#         if not username: 
#             return api_response(message="Username is required", code=400, status="error")

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor()
        
#         # 1. Generate MD5 Refresh Token
#         random_str = str(uuid.uuid4())
#         refresh_token = hashlib.md5(random_str.encode()).hexdigest()
        
#         ip = request.remote_addr
#         agent = request.headers.get('User-Agent')

#         # 2. Call Procedure: usp_v1_login_user
#         cur.execute("""
#             CALL login.usp_v1_login_user(
#                 %s, %s, %s, %s, %s, %s, 
#                 NULL::INTEGER, NULL::VARCHAR, NULL::JSONB, NULL::INTEGER, NULL::VARCHAR, NULL::INTEGER
#             )
#             """, 
#             (username, email, mobile, ip, agent, refresh_token)
#         )
#         result = cur.fetchone()

#         if result['p_status_code'] == 200:
#             # Create JWT Access Token
#             payload = {
#                 "sub": str(result['p_user_id']),
#                 "name": result['p_full_name_out'],
#                 "username": username,
#                 "roles": result['p_role_json'],
#                 "sid": str(result['p_session_id']),
#                 "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
#             }
#             token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
            
#             return api_response(message=result['p_message'], code=200, data={
#                 "token": token,
#                 "refresh_token": refresh_token, # This is the MD5 hash
#                 "user": payload
#             })
        
#         return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()



# =========================================================
# STEP 3: LOGIN (Generates MD5 Token)
# =========================================================
 

def login_login_user():
    """ POST /api/v1/auth/login """
    conn = None
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        mobile = data.get('mobile') or data.get('phone')

        if not username: 
            return api_response(message="Username is required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # 1. Generate MD5 Refresh Token
        random_str = str(uuid.uuid4())
        refresh_token = hashlib.md5(random_str.encode()).hexdigest()
        
        ip = request.remote_addr
        agent = request.headers.get('User-Agent')

        # 2. Call Procedure (13 Arguments)
        cur.execute("""
            CALL login.usp_v1_login_user(
                %s, %s, %s, %s, %s, %s, 
                NULL::INTEGER,   -- p_user_id
                NULL::VARCHAR,   -- p_full_name_out
                NULL::JSONB,     -- p_role_json (Now contains subscription_id)
                NULL::INTEGER,   -- p_session_id
                NULL::VARCHAR,   -- p_subscription_id
                NULL::VARCHAR,   -- p_message
                NULL::INTEGER    -- p_status_code
            )
            """, 
            (username, email, mobile, ip, agent, refresh_token)
        )
        result = cur.fetchone()

        if result['p_status_code'] == 200:
            # Create JWT Access Token
            payload = {
                "sub": str(result['p_user_id']),
                "name": result['p_full_name_out'],
                "username": username,
                "roles": result['p_role_json'], # This now includes the subscription_id per role
                "sid": str(result['p_session_id']),
                "sub_id": result['p_subscription_id'], 
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
            
            return api_response(message=result['p_message'], code=200, data={
                "token": token,
                "refresh_token": refresh_token,
                "user": payload, # The frontend will see the roles with subscription_id here
                "subscription_id": result['p_subscription_id']
            })
        
        return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()
        if conn: conn.close()