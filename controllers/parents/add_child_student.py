import jwt
from flask import request
from config import get_db_connection, JWT_SECRET
from utils.api_response import api_response

def add_child_student(): 
    """
    POST /user/add-child
    Extracts User ID from Token -> Checks Role -> Adds Student
    """
    conn = None
    try:
        # 1. EXTRACT TOKEN
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return api_response(message="Missing or Invalid Token", code=401, status="error")
        
        token = auth_header.split(" ")[1]

        # 2. DECODE TOKEN
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user_id = payload.get('sub') # 'sub' holds the user_id
            user_roles = payload.get('roles', []) # Expecting a list of role objects
        except jwt.ExpiredSignatureError:
            return api_response(message="Token has expired", code=401, status="error")
        except jwt.InvalidTokenError:
            return api_response(message="Invalid Token", code=401, status="error")

        # 3. CHECK PERMISSIONS (RBAC)
        # Allowed roles: super_admin, institute_admin, teacher, parent
        allowed_roles = ["super_admin", "institute_admin", "teacher", "parent"]
        
        # Check if user has at least one valid role
        # We assume 'user_roles' is a list of dicts like [{'role_name': 'teacher', ...}]
        # If your token stores just strings ['teacher'], adjust logic accordingly.
        has_permission = False
        for role in user_roles:
            # Handle both dictionary (from DB JSON) and string formats
            r_name = role.get('role_name') if isinstance(role, dict) else role
            if r_name in allowed_roles:
                has_permission = True
                break
        
        if not has_permission:
            return api_response(message="Access Denied: Role not authorized", code=403, status="error")

        # 4. GET INPUT DATA
        data = request.get_json()
        if not data:
            return api_response(message="No input data provided", code=400, status="error")

        name = data.get('name')
        email = data.get('email')
        mobile = data.get('mobile')

        if not name:
             return api_response(message="Student Name is required", code=400, status="error")
        if not email and not mobile:
             return api_response(message="Student Email or Mobile is required", code=400, status="error")

        # 5. DATABASE OPERATION
        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor()

        # Call Stored Procedure with Extracted ID
        cur.execute(
            "CALL sp_add_child_student(%s, %s, %s, %s, NULL::VARCHAR, NULL::INTEGER)", 
            (current_user_id, name, email, mobile)
        )
        result = cur.fetchone()

        if result and result.get('p_status_code') == 200:
            return api_response(message=result['p_message'], code=200)
        elif result:
            return api_response(message=result['p_message'], code=result['p_status_code'], status="error")
        else:
            return api_response(message="Database Error", code=500, status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()