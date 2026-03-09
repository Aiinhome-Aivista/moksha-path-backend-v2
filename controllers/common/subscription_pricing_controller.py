from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier

def get_subscription_plans_post():
    conn = None
    try:
        #  TOKEN CHECK
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(
                message="Unauthorized",
                code=401,
                status="error",
                error=auth_error
            )

        #  Payload (SAFE)
        data = request.get_json() or {}

        board_id = data.get("board_id")
        class_id = data.get("class_id")
        subject_ids = data.get("subject_ids")

        #  Validation
        if not board_id or not class_id:
            return api_response(
                message="board_id and class_id are required",
                code=400,
                status="error"
            )

        if not isinstance(subject_ids, list) or len(subject_ids) == 0:
            return api_response(
                message="subject_ids must be a non-empty list",
                code=400,
                status="error"
            )

        #  DB CALL
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            CALL subscription.usp_v2_get_user_subscription_plans(
                %s, %s, %s,
                NULL,
                NULL,
                NULL
            )
            """,
            (board_id, class_id, subject_ids)
        )

        result = cur.fetchone()

        return api_response(
            message=result["o_message"],
            code=result["o_status"],
            data=result["o_data"]
        )

    except Exception as e:
        print("REAL ERROR:", repr(e))
        return api_response(
            message="Internal Server Error",
            code=500,
            status="error",
            error=str(e)
        )
    finally:
        if conn:
            conn.close()
