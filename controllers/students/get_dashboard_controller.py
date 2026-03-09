from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras

def get_student_dashboard():
    """
    Fetches the Main Dashboard Overview.
    Route: GET /api/v1/learning/student/dashboard
    """
    try:
        # 1. Extract User ID from JWT Token
        user_id, error = TokenVerifier.get_user_id()
        if error: return api_response(message=error, code=401, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 2. Call the Stored Procedure
            cur.execute(
                "CALL learning.usp_v1_get_student_main_dashboard(%s, 0, '', '{}'::JSONB)",
                (user_id,)
            )
            result = cur.fetchone()
            conn.commit()

            if result and result['o_status'] == 200:
                return api_response(
                    message=result['o_message'], 
                    data=result['o_data'], 
                    code=200, 
                    status="success"
                )
            else:
                msg = result['o_message'] if result else "No data returned"
                return api_response(message=msg, code=result['o_status'] if result else 500, status="error")

        except Exception as db_err:
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")