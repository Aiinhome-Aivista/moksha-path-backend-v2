from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras
import json 
from utils.get_user_context import get_user_context   


 # ==========================================
# GET MAIN STUDENT DASHBOARD (Analytics UI)
# ==========================================
def get_main_dashboard():
    """
    GET /api/v1/learning/dashboard/main
    Returns the high-level analytics dashboard data.
    """
    try:
        # 1. Get User Context (Using your secure helper)
        user_id, subscription_id, error = get_user_context()
        if error: 
            return api_response(message=error, code=401, status="error")
        if not subscription_id:
            return api_response(message="Active subscription not found.", code=403, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 2. Call the new Stored Procedure
            cur.execute(
                """
                CALL report.usp_v1_get_student_main_dashboard(
                    %s::integer, 
                    %s::varchar, 
                    0, 
                    ''::text, 
                    '{}'::jsonb
                )
                """,
                (user_id, subscription_id)
            )
            result = cur.fetchone()
            conn.commit()

            if result['o_status'] == 200:
                return api_response(
                    message=result['o_message'], 
                    data=result['o_data'], 
                    code=200, 
                    status="success"
                )
            else:
                return api_response(
                    message=result['o_message'], 
                    code=result['o_status'], 
                    status="error"
                )

        except Exception as db_err:
            conn.rollback()
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")