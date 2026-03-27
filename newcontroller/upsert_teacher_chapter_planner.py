from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras
import jwt


def upsert_teacher_chapter_planner():
    conn = None
    try:
        # 🔐 AUTH (User ID from token)
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(
                message="Unauthorized",
                code=401,
                status="error",
                error=auth_error
            )

        user_id = int(user_id_str)

        # 🔐 Subscription Token
        sub_token = request.headers.get('Subscription-Token')
        if sub_token and "Bearer " in sub_token:
            sub_token = sub_token.split(" ")[1]

        # 📥 INPUT
        data = request.get_json() or {}

        chapter_id = data.get("chapter_id")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        is_completed = data.get("is_completed")  # optional

        # ❗ Basic Validation
        if not chapter_id:
            return api_response(
                message="chapter_id is required",
                code=400,
                status="error"
            )

        # 🛢 DB CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            CALL learning.usp_v1_teacher_chapter_planner_upsert(
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                NULL,
                NULL
            )
        """, (
            user_id,
            sub_token,
            chapter_id,
            start_date,
            end_date,
            is_completed
        ))

        result = cur.fetchone()

        return api_response(
            message=result.get("p_message"),
            code=result.get("p_status_code"),
            status="success" if result.get("p_status_code") == 200 else "error"
        )

    except Exception as e:
        return api_response(
            message="Internal Server Error",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if conn:
            conn.close()
            


def get_institute_admin_summary():
    conn = None
    try:
        # 1. Get Logged-in User ID from Main Token
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error")
        
        logged_in_user_id = int(user_id_str)
        
        # 2. Extract Subscription Code from Header Token
        sub_token = request.headers.get('subscription-token')
        if not sub_token:
            return api_response(message="Subscription-Id header missing", code=400, status="error")

        sub_payload = jwt.decode(sub_token, options={"verify_signature": False})
        subscription_code = sub_payload.get('sub_id') or sub_payload.get('subscription_id')

        # 3. Database Call
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Calling SP with 5 parameters (2 IN, 3 INOUT)
        cur.execute(
            "CALL learning.usp_get_institute_subscription_summary(%s, %s, NULL, NULL, NULL)",
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
        
        
        
def get_teacher_academic_data():

    conn = None

    try:
        #  AUTH (User Token)
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(
                message="Unauthorized",
                code=401,
                status="error",
                error=auth_error
            )

        teacher_user_id = int(user_id_str)

        #  Subscription Token
        sub_token = request.headers.get('Subscription-Token')
        if not sub_token:
            return api_response(
                message="Subscription-Token missing",
                code=400,
                status="error"
            )

        if "Bearer " in sub_token:
            sub_token = sub_token.split(" ")[1]

        # DB CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            """
            CALL learning.usp_new_get_teacher_academic_data(
                %s,
                %s,
                NULL,
                NULL,
                NULL
            )
            """,
            (teacher_user_id, sub_token)
        )

        result = cur.fetchone()

        return api_response(
            message=result.get("p_msg"),
            code=result.get("p_status_code"),
            data=result.get("p_object", []),
            status="success"
            if result.get("p_status_code") == 200
            else "error"
        )

    except Exception as e:

        return api_response(
            message="Internal Server Error",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if conn:
            conn.close()        