from flask import request
from config import get_db_connection, JWT_SECRET
import jwt
from utils.api_response import api_response

def get_token_user_id(req):
    # (Keep your existing helper function here)
    token = req.headers.get('Authorization')
    if not token: return None, "Missing Authorization Header"
    try:
        if "Bearer" in token: token = token.split(" ")[1]
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded.get('sub'), None
    except Exception as e: return None, str(e)

def save_academic_details():
    conn = None
    try:
        # 1. Auth Check
        user_id_str, auth_error = get_token_user_id(request)
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        user_id = int(user_id_str)

        # 2. Get Data (Allow Partial Data)
        data = request.get_json()
        
        board_name = data.get('board_name', '').strip() or None
        school_name = data.get('school_name', '').strip() or None
        class_name = data.get('class_name', '').strip() or None
        academic_year = data.get('academic_year', '').strip() or None

        # 3. Validation: Ensure at least ONE field is provided
        if not any([board_name, school_name, class_name, academic_year]):
             return api_response(message="Provide at least one detail to save.", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor()

        # 4. Call SP
        cur.execute(
            "CALL sp_save_academic_details(%s, %s, %s, %s, %s, %s, %s)", 
            (user_id, board_name, school_name, class_name, academic_year, None, None)
        )
        
        # 5. Get Output
        result = cur.fetchone()
        status = result['p_status'] if 'p_status' in result else result[0]
        message = result['p_message'] if 'p_message' in result else result[1]

        if status == 'success':
            return api_response(message=message, code=200)
        else:
            return api_response(message=message, code=400, status="error")

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))
    finally:
        if conn: conn.close()