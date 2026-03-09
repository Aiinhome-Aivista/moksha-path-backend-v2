from flask import request, jsonify
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription  # <--- Imported Helper
import psycopg2.extras
import json

# 1. API to Store Sample Questions (Used by AI or Admin)
def store_sample_questions():
    """ POST /api/v1/assessment/store-questions """
    try:
        data = request.get_json()
        questions = data.get('questions') # List of question objects

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute(
                "CALL learning.usp_v1_store_ai_questions(%s, 0, '')",
                (json.dumps(questions),)
            )
            result = cur.fetchone()
            conn.commit()
            return api_response(message=result['o_message'], code=result['o_status'])
        
        except Exception as e:
            conn.rollback()
            return api_response(message="DB Error", error=str(e), code=500)
        finally:
            cur.close(); conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500)

# 2. API to Start Assessment
def start_assessment():
    """ POST /api/v1/assessment/start """
    try:
        data = request.get_json()
        set_id = data.get('set_id')
        
        # Extract User ID
        user_id, error = TokenVerifier.get_user_id()
        if error: return api_response(message=error, code=401)

        # <--- Added Subscription Check Using Helper --->
        subscription_id = get_active_subscription(user_id)
        if not subscription_id:
            return api_response(message="Active Subscription ID not found for this user.", code=403, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # Note: Kept your existing SQL call exactly the same as requested. 
            # If your procedure needs the subscription_id in the future, you can pass it here.
            cur.execute(
                "CALL learning.usp_v1_start_assessment(%s, %s, 0, '', '{}'::JSONB)",
                (user_id, set_id)
            )
            result = cur.fetchone()
            conn.commit()
            
            return api_response(message=result['o_message'], data=result['o_data'], code=result['o_status'])

        except Exception as e:
            return api_response(message="DB Error", error=str(e), code=500)
        finally:
            cur.close(); conn.close()
    
    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500)

# 3. API to Submit Assessment
def submit_assessment():
    """ POST /api/v1/assessment/submit """
    try:
        data = request.get_json()
        attempt_id = data.get('attempt_id')
        answers = data.get('answers') # JSON Array

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute(
                "CALL learning.usp_v1_submit_assessment(%s, %s, 0, '', 0)",
                (attempt_id, json.dumps(answers))
            )
            result = cur.fetchone()
            conn.commit()

            return api_response(
                message=result['o_message'], 
                data={"score": result['o_score']}, 
                code=result['o_status']
            )

        except Exception as e:
            return api_response(message="DB Error", error=str(e), code=500)
        finally:
            cur.close(); conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500)