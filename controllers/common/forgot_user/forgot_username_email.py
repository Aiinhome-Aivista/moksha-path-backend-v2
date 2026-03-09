from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.email_sender import send_otp_email
from utils.sms_sender import send_sms_otp

# 1. SEND OTP
def recover_username_send_otp():
    conn = None
    try:
        data = request.get_json()
        email = data.get('email')
        mobile = data.get('mobile') or data.get('phone')

        if not email and not mobile:
            return api_response(message="Email or Mobile required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor()
        
        # Call Procedure
        cur.execute(
            "CALL login.usp_v1_forgot_username_send_otp(%s, %s, NULL::VARCHAR, NULL::VARCHAR, NULL::INTEGER)", 
            (email, mobile)
        )
        result = cur.fetchone()

        if result['p_status_code'] == 200:
            otp_code = result['p_otp_code']
            # Send Email/SMS logic here...
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

# 2. VERIFY OTP (THE FIX IS HERE)
def recover_username_verify():
    conn = None
    try:
        data = request.get_json()
        otp = data.get('otp')
        email = data.get('email')
        mobile = data.get('mobile') or data.get('phone')

        if not otp or (not email and not mobile):
            return api_response(message="OTP and (Email or Mobile) required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor()
        
        # -------------------------------------------------------------
        # CRITICAL FIX: You MUST use NULL::JSONB (Not VARCHAR)
        # -------------------------------------------------------------
        cur.execute(
            "CALL login.usp_v1_forgot_username_verify_otp(%s, %s, %s, NULL::JSONB, NULL::VARCHAR, NULL::INTEGER)", 
            (email, mobile, otp)
        )
        # -------------------------------------------------------------
        
        result = cur.fetchone()

        if result['p_status_code'] == 200:
            return api_response(
                message=result['p_message'], 
                code=200, 
                data={"usernames": result['p_username_list']} 
            )
            
        return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 3. GET EMAIL/MOBILE BY USERNAME (No OTP)
def get_user_details():
    """ POST /api/v1/auth/find-details """
    conn = None
    try:
        data = request.get_json()
        username = data.get('username')

        if not username:
            return api_response(message="Username required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor()
        
        cur.execute(
            "CALL login.usp_v1_get_details_by_username(%s, NULL::VARCHAR, NULL::VARCHAR, NULL::VARCHAR, NULL::INTEGER)", 
            (username,)
        )
        result = cur.fetchone()

        if result['p_status_code'] == 200:
            return api_response(
                message=result['p_message'], 
                code=200, 
                data={
                    "email": result['p_email'],
                    "mobile": result['p_mobile']
                }
            )
            
        return api_response(message=result['p_message'], code=result['p_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()