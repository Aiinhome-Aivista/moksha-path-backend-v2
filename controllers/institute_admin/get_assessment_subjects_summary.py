from flask import request
import jwt
import psycopg2.extras
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier

def get_institute_admin_summary():
    conn = None
    try:
        # 1. Get Logged-in User ID from Main Token
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error")
        
        logged_in_user_id = int(user_id_str)
        
        # 2. Extract Subscription Code from Header Token
        sub_token = request.headers.get('Subscription-Id')
        if not sub_token:
            return api_response(message="Subscription-Id header missing", code=400, status="error")

        sub_payload = jwt.decode(sub_token, options={"verify_signature": False})
        subscription_code = sub_payload.get('sub_id') or sub_payload.get('subscription_id')

        # 3. Database Call
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Calling SP with 5 parameters (2 IN, 3 INOUT)
        cur.execute(
            "CALL learning.usp_get_institute_subscription_summary_1(%s, %s, NULL, NULL, NULL)",
            (subscription_code, logged_in_user_id)
        )
        
        result = cur.fetchone()

        return api_response(
            message=result.get('o_message'),
            data=result.get('o_data', []),
            code=result.get('o_status', 200),
            status="success" if result.get('o_status') == 200 else "error"
        )

    except Exception as e:
        return api_response(message="Internal Server Error", error=str(e), code=500, status="error")
    finally:
        if conn: conn.close()



# from flask import request
# import jwt
# import psycopg2.extras
# from config import get_db_connection
# from utils.api_response import api_response
# from utils.token_helper import TokenVerifier

# def get_institute_admin_summary():
#     conn = None
#     try:
#         # Get user info from token
#         user_id_str, _ = TokenVerifier.get_user_id()
#         if not user_id_str:
#             return api_response(message="Unauthorized", code=401, status="error")
        
#         logged_in_user_id = int(user_id_str)
        
#         # Get subscription code from header
#         sub_token = request.headers.get('Subscription-Id')
#         sub_payload = jwt.decode(sub_token, options={"verify_signature": False})
#         subscription_code = sub_payload.get('sub_id') or sub_payload.get('subscription_id')

#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         cur.execute(
#             "CALL learning.usp_get_institute_subscription_summary_v1(%s, %s, NULL, NULL, NULL)",
#             (subscription_code, logged_in_user_id)
#         )
        
#         result = cur.fetchone()

#         return api_response(
#             message=result.get('o_message'),
#             data=result.get('o_data', []),
#             code=result.get('o_status', 200),
#             status="success" if result.get('o_status') == 200 else "error"
#         )

#     except Exception as e:
#         return api_response(message="Internal Server Error", error=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()