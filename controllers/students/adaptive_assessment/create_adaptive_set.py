from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras
import json
import jwt   

def create_adaptive_set():
    conn = None
    try:
        # =========================================================================
        # 1. AUTHENTICATION (Main User Token) quction will be set 2.5 basis
        # =========================================================================
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        logged_in_user_id = int(user_id_str)

        # =========================================================================
        # 2. EXTRACT SUBSCRIPTION ID FROM CUSTOM HEADER TOKEN
        # =========================================================================
        data = request.get_json()
        if not data:
            return api_response(message="Request body is empty", code=400, status="error")

        # Grab the token from the Header
        # sub_token = request.headers.get('Subscription-Id')
        sub_token = request.headers.get('Subscription-Id') or request.headers.get('Subscription-Token')

        if not sub_token:
            return api_response(message="Subscription-Id header is missing.", code=400, status="error")

        # Decode the token payload
        try:
            # We use verify_signature=False because we just need to read the data from it
            sub_payload = jwt.decode(sub_token, options={"verify_signature": False})
        except Exception as e:
            return api_response(message=f"Invalid subscription token: {str(e)}", code=400, status="error")

        # Find the default subscription_id
        subscription_id = None
        roles = sub_payload.get('roles', [])

        for role in roles:
            if role.get('is_default') is True:
                subscription_id = role.get('subscription_id')
                break

        # Fallback to sub_id if loop fails
        if not subscription_id:
            subscription_id = sub_payload.get('sub_id') or sub_payload.get('subscription_id')

        if not subscription_id:
            return api_response(message="Active Subscription ID not found for this user.", code=403, status="error")

        # =========================================================================
        # 3. DATABASE CALL
        # =========================================================================
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Step A: Create the Adaptive Assessment
        query_create = """
            CALL learning.usp_create_adaptive_assessment_v2(
                %s::INTEGER, %s::TEXT, %s::INTEGER, %s::INTEGER, %s::INTEGER, 
                %s::INTEGER, %s::INTEGER, %s::INTEGER, %s::INTEGER, %s::INTEGER, 
                %s::TEXT, %s::INTEGER[], %s::INTEGER[], %s::INTEGER[], 
                %s::TEXT, 
                NULL, NULL, NULL
            )
        """

        cur.execute(query_create, (
            logged_in_user_id,
            data.get('set_name', 'Adaptive Test'),
            data.get('institute_id'),
            data.get('board_id'),
            data.get('class_id'),
            data.get('subject_id'),
            data.get('total_marks'),
            data.get('duration_minutes'),
            data.get('number_of_questions'),
            data.get('max_attempt_count'),
            subscription_id,
            data.get('chapters_array', []),
            data.get('topics_array', []),
            data.get('student_ids', []),
            data.get('due_date') 
        ))

        result = cur.fetchone()

        res_status  = result.get('p_status', 'error')
        res_message = result.get('p_message', 'No message')
        res_data    = result.get('p_data', {})

        if res_status == 'success':
            # =========================================================================
            # 4. GENERATE INDIVIDUAL QUESTION SLOTS (NEW LOGIC)
            # =========================================================================
            # We use the set_id returned in p_data to populate the generation table
            new_set_id = res_data.get('set_id')

            if new_set_id:
                # Using BIGINT cast to support billions of records as requested
                cur.execute("CALL learning.usp_generate_question_slots(%s::BIGINT)", (new_set_id,))

            conn.commit()
            return api_response(message=res_message, data=res_data, code=200, status="success")
        else:
            conn.commit()
            return api_response(message=res_message, code=400, status="error")

    except Exception as e:
        if conn: conn.rollback()
        print(f"CRITICAL_DEBUG: {repr(e)}") 
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: 
            conn.close()
            cur.close()
