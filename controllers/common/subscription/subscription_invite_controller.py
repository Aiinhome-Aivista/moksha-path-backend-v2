from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras

# 1. SEND INVITE (Now using User ID)
def send_invite_by_id():
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        sender_id = int(user_id_str)

        data = request.get_json()
        sub_code = data.get('subscription_code')
        # UPDATED: Expecting user_id now
        target_user_id = data.get('target_user_id') 

        if not sub_code or not target_user_id:
            return api_response(message="Subscription code and target_user_id are required", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # UPDATED: Calling the new SP that accepts ID
        cur.execute("CALL subscription.sp_send_invite_by_id(%s, %s, %s, NULL, NULL)", 
                    (sender_id, sub_code, target_user_id))
        result = cur.fetchone()

        if result and result['o_status_code'] == 200:
            return api_response(message=result['o_message'], code=200)
        
        return api_response(message=result['o_message'], code=result['o_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 2. GET MY PENDING INVITES (No Logic Changes, just safety check)
def get_my_invites():
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        user_id = int(user_id_str)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL subscription.sp_get_my_invites(%s, NULL, NULL)", (user_id,))
        result = cur.fetchone()

        return api_response(message="Invites fetched", code=200, data=result['o_invites'])

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 3. RESPOND TO INVITE (Logic inside SP handles the transaction insert now)
def respond_invite_username():
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        user_id = int(user_id_str)

        data = request.get_json()
        token = data.get('invite_token')
        action = data.get('action') 

        if not token or action not in ['accept', 'reject']:
            return api_response(message="Invalid params", code=400, status="error")

        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL subscription.sp_respond_to_subscription_invite_v1(%s, %s, %s, NULL, NULL)", 
                    (user_id, token, action))
        result = cur.fetchone()

        if result and result['o_status_code'] == 200:
            return api_response(message=result['o_message'], code=200)
        
        return api_response(message=result['o_message'], code=result['o_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 4. GET INVITE HISTORY (Both Sent and Received, All Statuses)
def get_invite_history():
    conn = None
    try:
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        user_id = int(user_id_str)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Call the new SP with 5 parameters (1 IN, 4 OUT)
        cur.execute("""
            CALL subscription.sp_v1_get_invite_history(
                %s, NULL, NULL, NULL, NULL
            )
        """, (user_id,))
        
        result = cur.fetchone()

        if result and result['o_status_code'] == 200:
            return api_response(
                message=result['o_message'], 
                code=200, 
                data={
                    "received_invites": result['o_received_invites'],
                    "sent_invites": result['o_sent_invites']
                }
            )
        
        return api_response(message=result['o_message'], code=result['o_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

def undo_invite():
    """ 
    POST /api/v1/subscription/invite/undo
    """
    conn = None
    try:
        # 1. Auth Check
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        user_id = int(user_id_str)

        # 2. Get Payload
        data = request.get_json()
        invite_id = data.get('invite_id')

        if not invite_id:
            return api_response(message="invite_id is required", code=400, status="error")

        # 3. Connect to DB
        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 4. Call Stored Procedure
        cur.execute("""
            CALL subscription.sp_undo_subscription_invite(
                %s, %s, NULL, NULL
            )
        """, (user_id, invite_id))
        
        result = cur.fetchone()

        # 5. Handle Response
        if result and result['o_status_code'] == 200:
            return api_response(message=result['o_message'], code=200, status="success")
        
        return api_response(message=result['o_message'], code=result['o_status_code'], status="error")

    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()