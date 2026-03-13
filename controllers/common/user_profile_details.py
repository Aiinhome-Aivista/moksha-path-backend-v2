from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras

# =========================================================
# GET PROFILE DETAILS
# =========================================================
def get_user_profile():
    """ GET /api/v1/profile """
    conn = None
    try:
        # Get user from Auth Token
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        user_id = int(user_id_str)
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Call GET Procedure
        cur.execute("""
            CALL common.usp_get_user_profile(
                %s, NULL, NULL, NULL, NULL, NULL, NULL, NULL
            )
        """, (user_id,))
        result = cur.fetchone()
        
        if result['p_status_code'] == 200:
            data = {
                "full_name": result['p_full_name'],
                "email": result['p_email'],
                "mobile": result['p_mobile'],
                # Safely format date to YYYY-MM-DD for React input type="date"
                "dob": result['p_dob'].strftime('%Y-%m-%d') if result['p_dob'] else None,
                "address": result['p_address']
            }
            return api_response(message=result['p_message'], code=200, data=data, status="success")
            
        return api_response(message=result['p_message'], code=result['p_status_code'], status="error")
        
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn:
            cur.close()
            conn.close()

# =========================================================
# UPDATE PROFILE DETAILS
# =========================================================
def update_user_profile():
    """ 
    POST /api/v1/profile 
    Body: { "dob": "1995-08-25", "address": "123 Main St" }
    """
    conn = None
    try:
        # Get user from Auth Token
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        user_id = int(user_id_str)
        data = request.get_json() or {}
        
        # Only extract the editable fields
        dob = data.get("dob")
        address = data.get("address")
        
        # Prevent empty string from breaking PostgreSQL Date casting
        if not dob or str(dob).strip() == "":
            dob = None

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Call UPDATE Procedure (Now taking 5 parameters: 3 IN, 2 OUT)
        cur.execute("""
            CALL common.usp_update_user_profile(
                %s, %s, %s, NULL, NULL
            )
        """, (user_id, dob, address))
        result = cur.fetchone()
        
        if result['p_status_code'] == 200:
            return api_response(message=result['p_message'], code=200, status="success")
            
        return api_response(message=result['p_message'], code=result['p_status_code'], status="error")
        
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn:
            cur.close()
            conn.close()

# =========================================================
# GET ACADEMIC / STUDENT DETAILS
# =========================================================

def get_academic_details():
    """ 
    GET /api/v1/profile/academic
    Fetches Enrollment Date, Institute, Board, Class, Year, and Section for the active subscription.
    """
    conn = None
    try:
        token_payload = TokenVerifier.get_user_payload()
        if not token_payload:
            return api_response(message="Unauthorized", code=401, status="error")
        
        user_id = int(token_payload.get('sub'))
        subscription_id = token_payload.get('subscription_id') or token_payload.get('sub_id')

        if not subscription_id:
            return api_response(message="No active subscription found for this profile.", code=404, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # 2. Call the SP (Passing 2 inputs + 8 NULLs for outputs = 10 total)
        cur.execute("""
            CALL common.usp_get_academic_details(
                %s, %s, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
            )
        """, (user_id, subscription_id))
        result = cur.fetchone()
        
        if result['p_status_code'] == 200:
            
            # Format the date
            enrollment_date = None
            if result['p_enrollment_date']:
                enrollment_date = result['p_enrollment_date'].strftime('%d %b %Y')

            # Handle the PostgreSQL text[] array safely
            sections_data = result['p_sections']
            if sections_data and isinstance(sections_data, list) and len(sections_data) > 0:
                section_name = ", ".join(str(s) for s in sections_data)
            else:
                section_name = "N/A"

            data = {
                "enrollment_date": enrollment_date,
                "institute_name": result['p_institute_name'] or "N/A",
                "board_name": result['p_board_name'] or "N/A",
                "class_name": result['p_class_name'] or "N/A",
                "academic_year": result['p_academic_year'] or "N/A", # <-- ADDED THIS
                "section_name": section_name
            }
            return api_response(message=result['p_message'], code=200, data=data, status="success")
            
        return api_response(message=result['p_message'], code=result['p_status_code'], status="error")
        
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn:
            cur.close()
            conn.close()