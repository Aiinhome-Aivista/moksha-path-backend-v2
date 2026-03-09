from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription  # <--- Imported Helper
import psycopg2.extras

def update_priority():
    """
    POST /api/v1/learning/priority/update
    
    """
    try:
        # 1. Get User Payload
        payload = TokenVerifier.get_user_payload()
        if not payload:
            return api_response(message="Unauthorized", code=401, status="error")
            
        user_id = payload.get('sub')
        roles = payload.get('roles', [])

        # 2. Extract Subscription ID (From DB Helper) & Role Name (From Token)
        # <--- ALWAYS fetch latest subscription from DB --->
        subscription_id = get_active_subscription(user_id)
        user_role = None  # Start as None

        # A. Try to find the default role in the list to get the role name
        for role in roles:
            if role.get('is_default') is True:
                user_role = role.get('role_name') # Extract role from token
                break
        
        # If user_role is still None, try top level or default to 'Student' ONLY as last resort
        if not user_role:
            user_role = payload.get('role', 'Student') 

        # Validate we found what we needed
        if not subscription_id:
             return api_response(message="Active Subscription not found.", code=403, status="error")
        
        # Capitalize Role to match DB enum if needed (e.g. "student" -> "Student")
        if user_role:
            user_role = user_role.capitalize()

        # 3. Get Request Data
        data = request.get_json()
        chapter_id = data.get('chapter_id')
        
        # Normalize Priority Input (low -> Low)
        raw_priority = data.get('priority')
        new_priority = raw_priority.capitalize() if raw_priority else None

        if not chapter_id or not new_priority:
            return api_response(message="Chapter ID and Priority are required", code=400, status="error")

        allowed_priorities = ['High', 'Medium', 'Low']
        if new_priority not in allowed_priorities:
             return api_response(message=f"Invalid priority. Allowed: {allowed_priorities}", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 4. Call Procedure
            cur.execute(
                """
                CALL learning.usp_v1_update_chapter_priority(
                    %s::integer,   -- p_user_id
                    %s::varchar,   -- p_subscription_id
                    %s::integer,   -- p_chapter_id
                    %s::varchar,   -- p_new_priority
                    %s::varchar,   -- p_role_name (DYNAMICALLY EXTRACTED)
                    0,             -- o_status
                    ''::text       -- o_message
                )
                """,
                (user_id, subscription_id, chapter_id, new_priority, user_role)
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