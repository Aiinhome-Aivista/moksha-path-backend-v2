from flask import request
import psycopg2.extras
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response

# =========================================================
# API: GET CONTEXTUAL STUDENTS (For Teachers/Parents)
# =========================================================
def get_students_list_by_academics():
    """
    GET /api/v1/students/my-context
    Fetches all students that share the same board/class/institute as the logged-in user.
    Headers: Authorization: Bearer <jwt_token>
    """
    conn = None
    try:
        # 1. Verify User is Logged In and extract their secure payload
        payload = TokenVerifier.get_user_payload() 
        if not payload:
            return api_response(message="Unauthorized. Invalid or missing token.", code=401, status="error")
            
        # 2. Extract the Teacher/Parent's exact IDs from the token
        logged_in_user_id = payload.get('sub')
        
        # If UI wants to pass a specific subscription_id, let them, otherwise default to the active token sub_id
        subscription_id = request.args.get('subscription_id') or payload.get('sub_id')

        if not logged_in_user_id:
            return api_response(message="User ID missing from token.", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 3. Call Stored Procedure
        cur.execute(
            """
            CALL common.usp_v1_get_students_by_parent_teacher(
                %s::bigint, %s::varchar, 
                '{}'::jsonb, ''::varchar, 0::integer
            )
            """,
            (logged_in_user_id, subscription_id)
        )
        
        result = cur.fetchone()

        if result['o_status_code'] == 200:
            return api_response(
                message=result['o_message'], 
                code=200, 
                data=result['o_students'], 
                status="success"
            )
        else:
            return api_response(message=result['o_message'], code=result['o_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn:
            cur.close()
            conn.close()