from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier  
import psycopg2.extras


def add_parent_student_mapping():
    conn = None
    try:
        # ==========================================
        # 1. AUTHENTICATION CHECK
        # ==========================================
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        logged_in_user_id = int(user_id_str)

        # ==========================================
        # 2. DYNAMIC PAYLOAD MAPPING
        # ==========================================
        data = request.get_json()
        if not data:
            return api_response(message="Request body is empty", code=400, status="error")

        # Scenario A: Parent is calling the API to add a Student
        if 'student_user_id' in data:
            s_id = int(data.get('student_user_id', 0))
            p_id = logged_in_user_id  # Automatically assign token ID as Parent

        # Scenario B: Student is calling the API to add a Parent
        elif 'parent_user_id' in data:
            p_id = int(data.get('parent_user_id', 0))
            s_id = logged_in_user_id  # Automatically assign token ID as Student

        else:
            return api_response(message="Please provide either 'student_user_id' or 'parent_user_id' in the payload.", code=400, status="error")

        if p_id == 0 or s_id == 0:
            return api_response(message="Invalid User ID provided.", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # ==========================================
        # 3. CALL PROCEDURE
        # ==========================================
        query = """
            CALL common.usp_addparents_tudent_mapping_v1(
                %s::INTEGER, %s::INTEGER, %s::INTEGER, 
                NULL, NULL, NULL
            )
        """
        cur.execute(query, (logged_in_user_id, p_id, s_id))

        result = cur.fetchone()

        if not result:
            return api_response(message="Database returned no response", code=404, status="error")

        res_status  = result.get('p_status', 'error')
        res_message = result.get('p_message', 'No message')
        res_data    = result.get('p_data', None)

        # ==========================================
        # 4. RESPONSE HANDLING
        # ==========================================
        if res_status == 'success':
            return api_response(message=res_message, data=res_data, code=200, status="success")
        else:
            return api_response(message=res_message, data=res_data, code=400, status="error")

    except Exception as e:
        print(f"CRITICAL_DEBUG: {repr(e)}") 
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: 
            conn.close()
            cur.close()


def search_user_for_mapping():
    conn = None
    try:
        # 1. AUTHENTICATION
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        logged_in_user_id = int(user_id_str)

        # 2. VALIDATE PAYLOAD (Now completely optional!)
        # silent=True prevents errors if the body is completely empty
        data = request.get_json(silent=True) or {}
        search_term = str(data.get('search_term', '')).strip()

        # Notice: I removed the "len(search_term) < 2" error check!
        # If it's empty, it will just pass an empty string to the database.

        # 3. DATABASE CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            CALL common.sp_search_user_for_mapping_v1(
                %s::INTEGER, %s::TEXT, 
                NULL, NULL, NULL
            )
        """
        cur.execute(query, (logged_in_user_id, search_term))
        result = cur.fetchone()

        if not result:
            return api_response(message="Database returned no response", code=404, status="error")

        res_status  = result.get('p_status', 'error')
        res_message = result.get('p_message', 'No message')
        res_data    = result.get('p_data', [])

        if res_status == 'success':
            return api_response(message=res_message, data=res_data, code=200, status="success")
        else:
            return api_response(message=res_message, data=res_data, code=400, status="error")

    except Exception as e:
        print(f"CRITICAL_DEBUG: {repr(e)}") 
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: 
            conn.close()
            cur.close()


def manage_parent_student_mapping():
    conn = None
    try:
        # 1. AUTHENTICATION
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        logged_in_user_id = int(user_id_str)

        # 2. VALIDATE PAYLOAD
        data = request.get_json()
        if not data:
            return api_response(message="Request body is empty", code=400, status="error")

        link_id = int(data.get('link_id', 0))
        action = str(data.get('action', '')).upper() # 'ACCEPT' or 'DELETE'

        if link_id == 0 or action not in ['ACCEPT', 'DELETE']:
            return api_response(message="Valid link_id and action ('ACCEPT' or 'DELETE') are required.", code=400, status="error")

        # 3. DATABASE CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # query = """
        #     CALL common.sp_manage_parent_student_mapping(
        #         %s::INTEGER, %s::INTEGER, %s::VARCHAR,
        #         NULL, NULL, NULL
        #     )
        # """
        query = """
            CALL common.sp_manage_parent_student_mapping_v2(
                %s::INTEGER, %s::INTEGER, %s::VARCHAR, 
                NULL, NULL, NULL
            )
        """
        cur.execute(query, (logged_in_user_id, link_id, action))
        result = cur.fetchone()

        if not result:
            return api_response(message="Database returned no response", code=404, status="error")

        res_status  = result.get('p_status', 'error')
        res_message = result.get('p_message', 'No message')

        if res_status == 'success':
            return api_response(message=res_message, code=200, status="success")
        else:
            return api_response(message=res_message, code=400, status="error")

    except Exception as e:
        print(f"CRITICAL_DEBUG: {repr(e)}") 
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: 
            conn.close()
            cur.close()


def get_pending_mapping_requests():
    conn = None
    try:
        # 1. AUTHENTICATION
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        logged_in_user_id = int(user_id_str)

        # 2. DATABASE CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            CALL common.usp_get_pending_mapping_requests_v1(
                %s::INTEGER, 
                NULL, NULL, NULL
            )
        """
        cur.execute(query, (logged_in_user_id,))
        result = cur.fetchone()

        if not result:
            return api_response(message="Database returned no response", code=404, status="error")

        res_status  = result.get('p_status', 'error')
        res_message = result.get('p_message', 'No message')
        res_data    = result.get('p_data', [])

        if res_status == 'success':
            return api_response(message=res_message, data=res_data, code=200, status="success")
        else:
            return api_response(message=res_message, data=res_data, code=400, status="error")

    except Exception as e:
        print(f"CRITICAL_DEBUG: {repr(e)}") 
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: 
            conn.close()
            cur.close()


def get_invitation_all_summary():
    conn = None
    try:
        # 1. AUTHENTICATION
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        logged_in_user_id = int(user_id_str)

        # 2. DATABASE CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # query = """
        #     CALL common.usp_get_assigned_users_list_v1(
        #         %s::INTEGER,
        #         NULL, NULL, NULL
        #     )
        # """
        query = """
            CALL common.usp_get_assigned_users_list_v2(
                %s::INTEGER, 
                NULL, NULL, NULL
            )
        """
        cur.execute(query, (logged_in_user_id,))
        result = cur.fetchone()

        if not result:
            return api_response(message="Database returned no response", code=404, status="error")

        res_status  = result.get('p_status', 'error')
        res_message = result.get('p_message', 'No message')
        res_data    = result.get('p_data', {})

        if res_status == 'success':
            return api_response(message=res_message, data=res_data, code=200, status="success")
        else:
            return api_response(message=res_message, data=res_data, code=400, status="error")

    except Exception as e:
        print(f"CRITICAL_DEBUG: {repr(e)}") 
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: 
            conn.close()
            cur.close()


def get_active_user_student_parent_list():
    conn = None
    try:
        # 1. AUTHENTICATION
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        logged_in_user_id = int(user_id_str)

        # 2. DATABASE CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            CALL common.usp_get_active_user_mappings_v1(
                %s::INTEGER, 
                NULL, NULL, NULL
            )
        """
        cur.execute(query, (logged_in_user_id,))
        result = cur.fetchone()

        if not result:
            return api_response(message="Database returned no response", code=404, status="error")

        res_status  = result.get('p_status', 'error')
        res_message = result.get('p_message', 'No message')
        res_data    = result.get('p_data', [])

        if res_status == 'success':
            return api_response(message=res_message, data=res_data, code=200, status="success")
        else:
            return api_response(message=res_message, data=res_data, code=400, status="error")

    except Exception as e:
        print(f"CRITICAL_DEBUG: {repr(e)}") 
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: 
            conn.close()
            cur.close()


def create_and_map_dependent_profile():
    conn = None
    try:
        # 1. AUTHENTICATION
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        logged_in_user_id = int(user_id_str)

        # 2. PAYLOAD EXTRACTION
        data = request.get_json()
        if not data:
            return api_response(message="Request body is empty", code=400, status="error")

        # Basic Info (Optional Email/Phone)
        p_email = data.get('email', '')
        p_phone = data.get('phone', '')

        p_actual_name = data.get('actual_name', '')
        p_profile_name = data.get('profile_name', '')

        # Determine Role to Create (If creating Student = 1, Parent = 2)
        p_role_id = int(data.get('role_id', 0))

        # Academic Info (Mostly for students)
        p_board_id = data.get('board_id', None)
        p_class_id = data.get('class_id', None)
        p_institute_id = data.get('institute_id', None)

        if not p_actual_name or not p_profile_name or p_role_id not in [1, 2]:
            return api_response(message="Name, Profile Name, and valid Role ID (1 or 2) are required.", code=400, status="error")

        # 3. DATABASE CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            CALL common.sp_create_and_map_dependent_profile(
                %s::INTEGER, %s::VARCHAR, %s::VARCHAR, %s::VARCHAR, %s::VARCHAR, 
                %s::INTEGER, %s::INTEGER, %s::INTEGER, %s::INTEGER,
                NULL, NULL, NULL
            )
        """
        # Notice we removed subscription_id from the execute payload completely
        cur.execute(query, (
            logged_in_user_id, p_email, p_phone, p_actual_name, p_profile_name,
            p_role_id, p_board_id, p_class_id, p_institute_id
        ))
        result = cur.fetchone()

        if not result:
            return api_response(message="Database returned no response", code=404, status="error")

        res_status  = result.get('p_status', 'error')
        res_message = result.get('p_message', 'No message')
        res_data    = result.get('p_data', None)

        if res_status == 'success':
            return api_response(message=res_message, data=res_data, code=200, status="success")
        else:
            return api_response(message=res_message, data=res_data, code=400, status="error")

    except Exception as e:
        print(f"CRITICAL_DEBUG: {repr(e)}") 
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: 
            conn.close()
            cur.close()
