from flask import request
import psycopg2.extras
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.subscription_helper import get_active_subscription
from utils.api_response import api_response

# =========================================================
# API: GET STUDENT ASSESSMENTS
# =========================================================
def get_student_assessments_chapters_details():
    """
    GET /api/v1/learning/assessments
    Fetches all assigned assessments for the logged-in student, including chapter mappings.
    Headers: Authorization: Bearer <jwt_token>
    """
    conn = None
    try:
        # 1. Verify User is Logged In
        payload = TokenVerifier.get_user_payload() 
        if not payload:
            return api_response(message="Unauthorized. Invalid or missing token.", code=401, status="error")
            
        user_id = payload.get('sub')
        
        # Priority: explicit subscription_id from query params, then fallback to token/active sub
        subscription_id = request.args.get('subscription_id') or payload.get('sub_id') or get_active_subscription(user_id)

        if not user_id:
            return api_response(message="User ID missing from token.", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 2. Call Stored Procedure
        cur.execute(
            """
            CALL learning.usp_v1_get_student_assessments(
                %s::bigint, %s::varchar, 
                '{}'::jsonb, ''::varchar, 0::integer
            )
            """,
            (user_id, subscription_id)
        )
        
        result = cur.fetchone()

        if result['o_status_code'] == 200:
            return api_response(
                message=result['o_message'], 
                code=200, 
                data=result['o_assessments'], 
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