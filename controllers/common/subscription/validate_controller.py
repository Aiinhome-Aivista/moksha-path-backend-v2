from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras

def validate_subscription():
    """
    GET /api/v1/subscription/validate
    Checks if the logged-in user has a valid subscription.
    """
    try:
        # 1. Get User ID from Token
        user_id, error = TokenVerifier.get_user_id()
        if error: return api_response(message=error, code=401, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 2. Call Procedure
            cur.execute(
                "CALL subscription.usp_v1_validate_user_subscription(%s, 0, '', '{}'::JSONB)",
                (user_id,)
            )
            result = cur.fetchone()
            conn.commit()

            return api_response(
                message=result['o_message'], 
                data=result['o_data'], 
                code=200, 
                status="success"
            )

        except Exception as db_err:
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close(); conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")