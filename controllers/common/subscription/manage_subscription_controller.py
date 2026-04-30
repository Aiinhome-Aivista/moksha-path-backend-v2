from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras

def get_full_manage_subscription_page():
    """
    GET /api/v1/subscription/invitations/dashboard
    """
    conn = None
    try:
        # 1. Verify Token & Extract Payload
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        user_id = int(user_id_str)

        # 2. Call DB
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            CALL subscription.sp_v1_get_invitation_dashboard(
                %s, NULL, NULL, NULL
            )
        """, (user_id,))

        result = cur.fetchone()

        # 3. Handle Response
        if result and result['o_status_code'] == 200:
            return api_response(
                message=result['o_message'], 
                code=200, 
                status="success",
                data=result['o_data']
            )
        else:
            return api_response(
                message=result.get('o_message', 'Failed to fetch details'), 
                code=result.get('o_status_code', 400), 
                status="error"
            )

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")
    finally:
        if conn: 
            conn.close()
            cur.close()
