# from flask import request
# from config import get_db_connection
# from utils.api_response import api_response
# from utils.token_helper import TokenVerifier
# import psycopg2.extras

 
# # =========================================================
# # 1. GET API: Fetch ALL Academic Masters (No Dependency)
# # =========================================================
# def get_user_academic_details_nodependices():
#     """
#     GET /api/v1/academic/masters
#     Requires Login Token
#     Returns Boards, Schools, Classes, and Years all at once.
#     """
#     conn = None
#     try:
#         # 1. GLOBAL TOKEN CHECK
#         user_id_str, auth_error = TokenVerifier.get_user_id()
#         if not user_id_str:
#             return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         # 2. Call the new Stored Procedure
#         cur.execute("CALL master.usp_v2_get_academic_masters('', '', '{}'::jsonb)")
#         result = cur.fetchone()

#         # 3. Return the exact JSON built by the database
#         if result['p_status'] == 'success':
#             return api_response(
#                 message=result['p_message'], 
#                 code=200, 
#                 data=result['p_data']
#             )
#         else:
#             return api_response(
#                 message=result['p_message'], 
#                 code=400, 
#                 status="error"
#             )

#     except Exception as e:
#         return api_response(message="Internal Server Error", code=500, status="error", error=str(e))
#     finally:
#         if conn:
#             cur.close()
#             conn.close()





# # =========================================================
# # POST API: Add New Institute (School)
# # =========================================================
# def add_institute():
#     """
#     POST /api/v1/academic/institute/add
#     Requires Login Token
#     """
#     conn = None
#     try:
#         # 1. GLOBAL TOKEN CHECK
#         user_id_str, auth_error = TokenVerifier.get_user_id()
#         if not user_id_str:
#             return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

#         # 2. Get Data
#         data = request.get_json()
#         school_name = data.get('school_name', '').strip()

#         if not school_name:
#             return api_response(message="School name is required", code=400, status="error")

#         conn = get_db_connection()
#         conn.autocommit = True
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         # 3. Call Stored Procedure
#         cur.execute(
#             "CALL master.usp_v1_add_institute(%s, '', '', '{}'::jsonb)", 
#             (school_name,)
#         )
#         result = cur.fetchone()

#         # 4. Format Response
#         if result['p_status'] == 'success':
#             return api_response(
#                 message=result['p_message'], 
#                 code=200, 
#                 data=result['p_data'],
#                 status="success"
#             )
#         else:
#             # Return 409 Conflict if it's a duplicate
#             return api_response(
#                 message=result['p_message'], 
#                 code=409, 
#                 status="error"
#             )

#     except Exception as e:
#         return api_response(message="Internal Server Error", code=500, status="error", error=str(e))
#     finally:
#         if conn:
#             cur.close()
#             conn.close()







from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras

# =========================================================
# 1. GET API: Fetch Flat Array of Academic Mappings
# =========================================================
def get_user_academic_details_nodependices():
    """
    GET /api/v1/academic/masters
    Requires Login Token
    Returns a single flat array of all valid Institute-Board-Class combinations.
    """
    conn = None
    try:
        # 1. GLOBAL TOKEN CHECK
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 2. Call the Stored Procedure (EXACTLY 3 ARGUMENTS cast to proper types)
        cur.execute("CALL master.usp_v2_get_academic_masters2(''::text, ''::text, '[]'::jsonb)")
        
        result = cur.fetchone()

        # 3. Return the Data
        if result['p_status'] == 'success':
            return api_response(
                message=result['p_message'], 
                code=200, 
                data=result['p_data'],
                status="success"
            )
        else:
            return api_response(
                message=result['p_message'], 
                code=400, 
                status="error"
            )

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))
    finally:
        if conn:
            cur.close()
            conn.close()





# =========================================================
# POST API: Add New Institute (School)
# =========================================================
def add_institute():
    """
    POST /api/v1/academic/institute/add
    Requires Login Token
    """
    conn = None
    try:
        # 1. GLOBAL TOKEN CHECK
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        # 2. Get Data
        data = request.get_json()
        school_name = data.get('school_name', '').strip()

        if not school_name:
            return api_response(message="School name is required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 3. Call Stored Procedure
        cur.execute(
            "CALL master.usp_v1_add_institute(%s, '', '', '{}'::jsonb)", 
            (school_name,)
        )
        result = cur.fetchone()

        # 4. Format Response
        if result['p_status'] == 'success':
            return api_response(
                message=result['p_message'], 
                code=200, 
                data=result['p_data'],
                status="success"
            )
        else:
            # Return 409 Conflict if it's a duplicate
            return api_response(
                message=result['p_message'], 
                code=409, 
                status="error"
            )

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))
    finally:
        if conn:
            cur.close()
            conn.close()

