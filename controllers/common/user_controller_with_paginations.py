from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier  
import psycopg2.extras
import math

 
def get_all_usernames_with_paginations():
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
        # 2. EXTRACT PAYLOAD PARAMS
        # ==========================================
        data = request.json or {}
        page = int(data.get('page', 1))        
        limit = int(data.get('limit', 10))     
        search = data.get('search', '')        
        class_ids = data.get('class_ids', [])  # <--- NEW: Extract class array (defaults to empty [])
        
        offset = (page - 1) * limit

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # ==========================================
        # 3. Call the Stored Procedure (Added class_ids)
        # ==========================================
        cur.execute("""
            CALL common.sp_get_all_usernames_paginated(
                %s, %s, %s, %s, %s,
                NULL, NULL, NULL, NULL
            )
        """, (logged_in_user_id, limit, offset, search, class_ids))
        
        result = cur.fetchone()

        # 4. Handle Response
        if result and result.get('p_status') == 'success':
            total_records = result.get('p_total_count', 0)
            total_pages = math.ceil(total_records / limit) if limit > 0 else 1

            return api_response(
                message=result.get('p_message'), 
                code=200, 
                status="success",
                data={
                    "users": result.get('p_usernames', []),
                    "pagination": {
                        "current_page": page,
                        "limit": limit,
                        "total_records": total_records,
                        "total_pages": total_pages
                    }
                }
            )
        else:
            return api_response(
                message=result.get('p_message', 'Failed to fetch usernames'), 
                code=400, 
                status="error"
            )

    except Exception as e:
        return api_response(
            message="Internal Server Error", 
            code=500, 
            status="error", 
            error=str(e)
        )
    finally:
        if conn: 
            conn.close()