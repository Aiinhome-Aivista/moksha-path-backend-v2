import jwt
import psycopg2.extras
from flask import request

from config import get_db_connection, JWT_SECRET
from utils.api_response import api_response
from utils.token_helper import TokenVerifier

# ==========================================
# POST: ASSIGN TEACHER (Institute Admin)
# ==========================================
def assign_teacher():
    """ POST /api/v1/institute_admin/assign_teacher """
    conn = None
    cur = None
    try:
        # ================= 1. VERIFY MAIN AUTH TOKEN =================
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        admin_user_id = int(user_id_str)

        # ================= 2. VERIFY SUBSCRIPTION TOKEN =================
        data = request.get_json() or {}
        
        sub_token = request.headers.get('Subscription-Token') or request.headers.get('X-Subscription-Token') or data.get("subscription_token")

        if not sub_token:
            return api_response(message="Subscription Token is missing", code=401, status="error")

        if "Bearer " in sub_token:
            sub_token = sub_token.split(" ")[1]

        # NEW: Check if the frontend accidentally sent the short SUB-ID instead of the long JWT token
        if len(sub_token.split('.')) != 3:
            return api_response(
                message="FRONTEND ERROR: You passed the Subscription ID (SUB-XXX) instead of the long JWT Subscription Token in the headers.", 
                code=400, 
                status="error"
            )

        try:
            sub_payload = jwt.decode(sub_token, JWT_SECRET, algorithms=["HS256"])
            admin_subscription_id = sub_payload.get("subscription_id") or sub_payload.get("sub_id")
            
            if not admin_subscription_id:
                return api_response(message="Invalid Subscription Token payload", code=401, status="error")
                
        except jwt.ExpiredSignatureError:
            return api_response(message="Subscription session expired", code=401, status="error")
        except jwt.InvalidTokenError:
            return api_response(message="Invalid Subscription Token", code=401, status="error")

        # ================= 3. GET REQUEST DATA =================
        teacher_user_id = data.get("teacher_user_id")
        
        # Array data for classes and sections (default to empty lists if missing)
        class_ids = data.get("class_ids", [])
        section_names = data.get("section_names", [])

        if not teacher_user_id:
            return api_response(message="Teacher User ID is required", code=400, status="error")

        if not isinstance(class_ids, list) or not isinstance(section_names, list):
            return api_response(message="class_ids and section_names must be arrays/lists", code=400, status="error")

        # ================= 4. DATABASE EXECUTION =================
        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Pass the 5 inputs + 2 outputs = 7 parameters
        cur.execute("""
            CALL common.usp_institute_add_teacher_v1(
                %s, %s, %s, %s, %s, 
                NULL, NULL
            )
        """, (admin_user_id, admin_subscription_id, teacher_user_id, class_ids, section_names))
        
        result = cur.fetchone()
        
        if not result:
            return api_response(message="Database returned no response", code=500, status="error")
        
        if result.get('p_status_code') == 200:
            return api_response(message=result.get('p_message'), code=200, status="success")
            
        return api_response(message=result.get('p_message'), code=result.get('p_status_code', 400), status="error")
        
    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# ==========================================
# POST: REMOVE TEACHER (Institute Admin)
# ==========================================
def remove_teacher():
    """ POST /api/v1/institute_admin/remove_teacher """
    conn = None
    cur = None
    try:
        # ================= 1. VERIFY MAIN AUTH TOKEN =================
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        admin_user_id = int(user_id_str)

        # ================= 2. VERIFY SUBSCRIPTION TOKEN =================
        data = request.get_json() or {}
        
        sub_token = request.headers.get('Subscription-Token') or request.headers.get('X-Subscription-Token') or data.get("subscription_token")

        if not sub_token:
            return api_response(message="Subscription Token is missing", code=401, status="error")

        # Fix: Remove 'Bearer ' if the frontend accidentally added it
        if "Bearer " in sub_token:
            sub_token = sub_token.split(" ")[1]

        if len(sub_token.split('.')) != 3:
            return api_response(
                message="FRONTEND ERROR: You passed the Subscription ID (SUB-XXX) instead of the long JWT Subscription Token in the headers.", 
                code=400, 
                status="error"
            )

        try:
            sub_payload = jwt.decode(sub_token, JWT_SECRET, algorithms=["HS256"])
            admin_subscription_id = sub_payload.get("subscription_id") or sub_payload.get("sub_id")
            
            if not admin_subscription_id:
                return api_response(message="Invalid Subscription Token payload", code=401, status="error")
                
        except jwt.ExpiredSignatureError:
            return api_response(message="Subscription session expired", code=401, status="error")
        except jwt.InvalidTokenError:
            return api_response(message="Invalid Subscription Token", code=401, status="error")

        # ================= 3. GET REQUEST DATA =================
        teacher_user_id = data.get("teacher_user_id")

        if not teacher_user_id:
            return api_response(message="Teacher User ID is required", code=400, status="error")

        # ================= 4. DATABASE EXECUTION =================
        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Call the SP (3 inputs + 2 outputs = 5 parameters)
        cur.execute("""
            CALL common.usp_institute_remove_teacher(%s, %s, %s, NULL, NULL)
        """, (admin_user_id, admin_subscription_id, teacher_user_id))
        
        result = cur.fetchone()
        
        if not result:
            return api_response(message="Database returned no response", code=500, status="error")
            
        if result.get('p_status_code') == 200:
            return api_response(message=result.get('p_message'), code=200, status="success")
            
        return api_response(message=result.get('p_message'), code=result.get('p_status_code', 400), status="error")
        
    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()