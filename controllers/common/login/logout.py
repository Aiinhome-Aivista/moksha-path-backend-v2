import jwt
import datetime
import uuid
import hashlib
from flask import request
from config import get_db_connection, JWT_SECRET
from utils.api_response import api_response 

# =========================================================
# STEP 4: LOGOUT USER (New)
# =========================================================
def login_logout_user():
    """ POST /api/v1/auth/logout """
    conn = None
    try:
        # 1. Get User ID from JWT Token (using your existing logic/helper)
        # For simplicity assuming you parse the token here or use a decorator
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return api_response(message="Missing Token", code=401, status="error")
        
        token = auth_header.split(" ")[1]
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_exp": False})
        user_id = decoded.get("sub")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor()

        # 2. Call Logout Procedure
        cur.execute("CALL login.usp_v1_logout_user(%s, NULL::VARCHAR, NULL::INTEGER)", (user_id,))
        result = cur.fetchone()

        return api_response(message=result['o_message'], code=result['o_status_code'])

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()