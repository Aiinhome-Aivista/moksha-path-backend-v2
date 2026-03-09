from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier  # <--- Import the new helper

# =========================================================
# 1. GET API: Fetch Cascading Master Data (Secured)
# =========================================================
def get_academic_masters():
    """
    GET /academic/masters
    Requires Login Token
    """
    conn = None
    try:
        # ---------------------------------------------------------
        # GLOBAL TOKEN CHECK
        # ---------------------------------------------------------
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        # ---------------------------------------------------------

        # 1. Get Query Params
        board_id_str = request.args.get('board_id')
        school_id_str = request.args.get('school_id')
        class_id_str = request.args.get('class_id')

        # Convert to Int or None
        p_board_id = int(board_id_str) if board_id_str and board_id_str.strip() else None
        p_school_id = int(school_id_str) if school_id_str and school_id_str.strip() else None
        p_class_id = int(class_id_str) if class_id_str and class_id_str.strip() else None

        conn = get_db_connection()
        conn.autocommit = False 
        cur = conn.cursor()

        try:
            # 2. Call Stored Procedure
            cursor_name = 'academic_cursor'
            cur.execute(
                "CALL master.usp_v1_get_academic_masters(%s, %s, %s, %s)", 
                (p_board_id, p_school_id, p_class_id, cursor_name)
            )

            # 3. Fetch Data
            cur.execute(f'FETCH ALL FROM "{cursor_name}"')
            rows = cur.fetchall()
            conn.commit() 

            # 4. Format Response
            data = []
            message = ""

            if p_board_id is None:
                data = [{'id': r['id'], 'name': r['name']} for r in rows]
                message = "Boards fetched successfully"
            
            elif p_school_id is None:
                data = [{'id': r['id'], 'name': r['name']} for r in rows]
                message = "All Schools fetched successfully"
                
            elif p_class_id is None:
                data = [{'id': r['id'], 'name': r['name']} for r in rows]
                message = "Classes fetched successfully"
                
            else:
                data = [{'year': r['name']} for r in rows]
                message = "Academic Years fetched successfully"

            return api_response(message=message, code=200, data=data)

        except Exception as query_error:
            conn.rollback()
            raise query_error

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))
    finally:
        if conn: conn.close()

# =========================================================
# 2. SAVE API: Save User Selection (Secured)
# =========================================================
def save_academic_details():
    """
    POST /academic/save
    Requires Login Token
    """
    conn = None
    try:
        # ---------------------------------------------------------
        # GLOBAL TOKEN CHECK
        # ---------------------------------------------------------
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        user_id = int(user_id_str)
        # ---------------------------------------------------------

        # Get Data
        data = request.get_json()
        board_name = data.get('board_name', '').strip() or None
        school_name = data.get('school_name', '').strip() or None
        class_name = data.get('class_name', '').strip() or None
        academic_year = data.get('academic_year', '').strip() or None

        if not any([board_name, school_name, class_name, academic_year]):
             return api_response(message="Provide at least one detail to save.", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(
            "CALL master.sp_save_academic_details(%s, %s, %s, %s, %s, %s, %s)", 
            (user_id, board_name, school_name, class_name, academic_year, None, None)
        )
        
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