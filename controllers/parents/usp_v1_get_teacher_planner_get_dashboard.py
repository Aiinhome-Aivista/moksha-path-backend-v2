from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras

def get_teacher_learning_planner_dashboard():
    """
    GET /api/v1/learning/dashboard
    Works dynamically for Teachers, prioritizing the "is_default": true subscription.
    """
    try:
        # 1. Get User Payload
        payload = TokenVerifier.get_user_payload()
        if not payload:
            return api_response(message="Unauthorized", code=401, status="error")
            
        user_id = int(payload.get('sub'))
        roles = payload.get('roles', [])

        # 2. Extract ONLY the Default Subscription ID from the roles array
        subscription_id = None
        for role in roles:
            if role.get('is_default') is True:
                subscription_id = role.get('subscription_id')
                break
        
        # Fallback to global sub_id if something goes wrong
        if not subscription_id:
            subscription_id = payload.get('sub_id')

        if not subscription_id:
            return api_response(
                message="Active Default Subscription not found in token.", 
                code=403, 
                status="error"
            )

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 3. Call Procedure with Subscription ID
            cur.execute(
                """
                CALL learning.usp_v1_get_teacher_planner_get_dashboard(
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
                return api_response(message=result['o_message'], data=result['o_data'], code=200, status="success")
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