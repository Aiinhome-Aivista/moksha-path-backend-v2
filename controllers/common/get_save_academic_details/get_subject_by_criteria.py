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
 

# def get_subjects_by_criteria():
#     conn = None
#     try:
#         user_id_str, auth_error = get_token_user_id(request)
#         if not user_id_str:
#             return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

#         data = request.get_json()
#         if not data:
#             return api_response(message="Request body is empty", code=400, status="error")

#         # Extraction from JSON
#         inst_name = data.get('institute_name')
#         board = data.get('board_name')
#         cls_name = data.get('class_name')
#         year = data.get('academic_year') # "2025-2026"

#         if not all([inst_name, board, cls_name, year]):
#             return api_response(message="Missing required filters", code=400, status="error")

#         conn = get_db_connection()
#         conn.autocommit = False 
#         cur = conn.cursor()

#         cursor_name = 'subject_results_cursor'

#         # 1. Procedure call
#         cur.execute(
#             "CALL master.sp_vi_get_subjects_by_criteria_s(%s, %s, %s, %s, %s)", 
#             (inst_name, board, year, cls_name, cursor_name)
#         )

#         # 2. Fetch data from cursor
#         cur.execute(f'FETCH ALL IN "{cursor_name}"')
#         rows = cur.fetchall()

#         # 3. Dynamic Mapping: Row tuple holeo hobe, dictionary holeo hobe
#         subjects = []
#         if rows:
#             for r in rows:
#                 # Eikhane logic ta simple kore dilam jate KeyError na ashe
#                 if isinstance(r, dict):
#                     subjects.append({
#                         "subject_id": r.get('subject_id'),
#                         "subject_name": r.get('subject_name')
#                     })
#                 else:
#                     subjects.append({
#                         "subject_id": r[0],
#                         "subject_name": r[1]
#                     })

#         conn.commit()
#         return api_response(message="Subjects retrieved successfully", data=subjects, code=200)

#     except Exception as e:
#         if conn: conn.rollback()
#         error_type = repr(e)
#         print(f"ASOL ERROR: {error_type}") 
#         return api_response(message="Internal Server Error", code=500, status="error", error=error_type)
#     finally:
#         if conn:
#             conn.close()


def get_subjects_by_criteria():
    conn = None
    try:
        data = request.get_json()
        if not data:
            return api_response(message="Request body is empty", code=400, status="error")

        # PAYLOAD NAME FIX: Ekhane key gulo eksathe match kora hoyeche
        # Tumi payload-e pathachho 'institute_name', tai data.get-eo shetai hobe
        i_id   = int(data.get('institute_name', 0))
        b_id   = int(data.get('board_name', 0))
        c_id   = int(data.get('class_name', 0))
        a_year = str(data.get('academic_year', ''))

        conn = get_db_connection()
        conn.autocommit = True 
        cur = conn.cursor()

        # Procedure Call with Casting
        # Procedure-er parameter sequence: p_institute_id, p_board_id, p_class_id, p_academic_year
        # query = """
        #     CALL master.sp_vi_get_subjects_by_criteria_s_V2(
        #         %s::INTEGER, %s::INTEGER, %s::INTEGER, %s::VARCHAR, 
        #         NULL, NULL, NULL
        #     )
        # """
        query = """
            CALL master.sp_v1_get_subjects_by_criteria(
                %s::INTEGER, %s::INTEGER, %s::INTEGER, %s::VARCHAR, 
                NULL, NULL, NULL
            )
        """
        cur.execute(query, (i_id, b_id, c_id, a_year))

        # Safe Fetch
        result = cur.fetchone()

        if not result:
            return api_response(message="Database returned no response", code=404, status="error")

        # Index check logic
        if isinstance(result, (list, tuple)):
            res_status  = result[0] if len(result) > 0 else 'error'
            res_message = result[1] if len(result) > 1 else 'Unknown Error'
            res_data    = result[2] if len(result) > 2 else None
        else:
            res_status  = result.get('p_status', 'error')
            res_message = result.get('p_message', 'No message')
            res_data    = result.get('p_data', None)

        if res_status == 'success':
            return api_response(message=res_message, data=res_data, code=200)
        else:
            # Jodi subjects na thake, res_data-te 'subjects': [] thakbe
            return api_response(message=res_message, data=res_data, code=404, status="error")

    except Exception as e:
        print(f"CRITICAL_DEBUG: {repr(e)}") 
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: conn.close()