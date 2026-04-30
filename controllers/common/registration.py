
from flask import request, jsonify
from config import get_db_connection

def register_user():
    """
    Controller to handle user registration.
    Extracts data from request, calls DB, and returns JSON response.
    """
    conn = None
    try:
        # 1. Extract Data from Request
        data = request.get_json()
        if not data:
             return jsonify({"status": "error", "message": "No input data provided", "code": 400}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        full_name = data.get('full_name')
        email = data.get('email')
        phone = data.get('phone')
        role_name = data.get('role_name')
        institute_id = data.get('institute_id') 
        subscription_id = data.get('subscription_id') 

        # 2. Call Stored Procedure
        sql = """
            CALL sp_register_user(%s, %s, %s, %s, %s, %s, NULL, NULL, NULL)
        """
        cur.execute(sql, (full_name, email, phone, role_name, institute_id, subscription_id))
        
        result = cur.fetchone()

        code = result.get('p_status_code')
        message = result.get('p_message')
        user_id = result.get('p_user_id')

        status_text = "success" if code < 400 else "error"

        response_body = {
            "status": status_text,
            "code": code,
            "message": message,
            "data": {"user_id": user_id} if code == 201 else None
        }

        # 3. Return Flask Response
        return jsonify(response_body), code

    except Exception as e:
        return jsonify({
            "status": "error",
            "code": 500,
            "message": "Internal Server Error",
            "error": str(e),
            "data": None
        }), 500
    finally:
        if conn:
            conn.close()
            cur.close()