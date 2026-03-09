from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription  # <--- Imported Helper
import psycopg2.extras

# ==========================================
# HELPER FUNCTION
# ==========================================
def get_user_context():
    """
    Extracts User ID from the Token and fetches the active Subscription ID from DB.
    Returns: (user_id, subscription_id, error_message)
    """
    payload = TokenVerifier.get_user_payload()
    if not payload: 
        return None, None, "Unauthorized"
    
    user_id = payload.get('sub')
    
    # ALWAYS fetch latest subscription from DB
    subscription_id = get_active_subscription(user_id)
        
    return user_id, subscription_id, None


# ==========================================
# API: Update Study Hours
# ==========================================
def update_study_hours():
    """
    Updates student's daily study capacity via USP.
    Route: POST /api/student/update-study-hours
    """
    try:
        # 1. Get User Context (Using the helper function)
        user_id, subscription_id, error = get_user_context()
        if error: return api_response(message=error, code=401, status="error")
        
        # Security check: Prevent updates if subscription is expired/missing
        if not subscription_id:
            return api_response(message="No active subscription found.", code=403, status="error")

        data = request.get_json() or {}
        new_hours = data.get('daily_study_hours') # Expecting float/int (e.g., 8.0)
        
        # Basic Validation
        if new_hours is None:
            return api_response(message="daily_study_hours is required.", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # Call USP_V1
            # Note: Kept parameters as (user_id, new_hours). If your SP requires subscription_id later, you can add it here.
            cur.execute(
                "CALL subscription.usp_v1_update_student_study_hours(%s, %s, 0, '')",
                (user_id, new_hours)
            )
            
            result = cur.fetchone()
            conn.commit()

            if result:
                 # result keys match INOUT names: o_status, o_message
                return api_response(
                    message=result['o_message'], 
                    code=result['o_status'], 
                    status="success" if result['o_status'] == 200 else "error"
                )
            else:
                return api_response(message="No response from DB", code=500, status="error")

        except Exception as db_err:
            conn.rollback()
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")