from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription  # <--- Imported Helper
import psycopg2.extras
import json

# ==========================================
# HELPER FUNCTION (Updated to use DB Helper)
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
    
    # <--- ALWAYS fetch latest subscription from DB --->
    subscription_id = get_active_subscription(user_id)
        
    return user_id, subscription_id, None


# ==========================================
# API: Update Topic Status (Bulk or Single)
# ==========================================
def update_topic_status():
    """
    POST /api/v1/learning/topic-status/bulk
    Body: [{"topic_id": 1, "chapter_id": 10, "status": "Completed"}]
    OR: {"topic_id": 1, "chapter_id": 10, "status": "Completed"} (Single Object)
    """
    try:
        # 1. Get User Context (Using the helper function)
        user_id, subscription_id, error = get_user_context()
        if error: 
            return api_response(message=error, code=401, status="error")
        if not subscription_id: 
            return api_response(message="Active Default Subscription not found.", code=403, status="error")

        # 2. Get JSON Body & FIX DATA STRUCTURE
        updates = request.get_json()
        
        if not updates:
            return api_response(message="No updates provided", code=400, status="error")

        # CRITICAL FIX: Ensure 'updates' is a LIST. If it's a DICT, wrap it.
        if isinstance(updates, dict):
            updates = [updates] 
        
        # Double check it is a list now
        if not isinstance(updates, list):
             return api_response(message="Invalid data format. Expected a list or object.", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 3. Call Procedure
            cur.execute(
                """
                CALL learning.usp_v1_update_bulk_topic_status(
                    %s::integer, 
                    %s::varchar, 
                    %s::jsonb, 
                    0, 
                    ''::text
                )
                """,
                # json.dumps(updates) converts the Python List -> JSON String "[{...}]"
                (user_id, subscription_id, json.dumps(updates))
            )
            
            result = cur.fetchone()
            conn.commit()

            if result['o_status'] == 200:
                return api_response(message=result['o_message'], code=200, status="success")
            else:
                return api_response(message=result['o_message'], code=result['o_status'], status="error")

        except Exception as db_err:
            conn.rollback()
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")