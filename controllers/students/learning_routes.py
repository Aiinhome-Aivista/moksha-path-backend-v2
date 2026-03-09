from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response

def get_learning_planner_old():
    """
    Controller to fetch the Student Learning Planner Dashboard.
    Route: POST /api/student/learning-planner
    """
    try:
        # 1. Authenticate User
        user_id, error = TokenVerifier.get_user_id()
        if error:
            return api_response(message=error, code=401, status="error")

        # 2. Get Inputs
        data = request.get_json() if request.is_json else {}
        subject_id = data.get('subject_id')  # Can be None

        # 3. Database Interaction
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            # ---------------------------------------------------------
            # FIX IS HERE: Added ::INTEGER, ::TEXT, ::JSONB casts
            # ---------------------------------------------------------
            cur.execute(
                """
                CALL learning.usp_v1_get_learning_planner(
                    %s::INTEGER, 
                    %s::INTEGER, 
                    %s::INTEGER, 
                    %s::TEXT, 
                    %s::JSONB
                )
                """,
                (user_id, subject_id, 0, '', None)
            )

            # Fetch the INOUT results
            result = cur.fetchone()
            conn.commit()

        except Exception as db_err:
            conn.rollback()
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close()
            conn.close()

        # 4. Process Response
        if result:
            db_status = result['o_status']
            db_message = result['o_message']
            db_data = result['o_data']

            if db_status == 200:
                return api_response(data=db_data, message=db_message, code=200, status="success")
            else:
                return api_response(message=db_message, code=db_status, status="error")
        else:
            return api_response(message="No data returned from database.", code=500, status="error")

    except Exception as e:
        return api_response(message="Internal Server Error", error=str(e), code=500, status="error")