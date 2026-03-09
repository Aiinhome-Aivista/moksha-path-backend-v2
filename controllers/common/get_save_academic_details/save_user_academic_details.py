from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
from psycopg2.extras import RealDictCursor


def save_user_academic_details():

    conn = None
    try:
        #  Token Validation
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(
                message="Unauthorized",
                code=401,
                status="error",
                error=auth_error
            )

        user_id = int(user_id_str)
        data = request.get_json() or {}

        board_id = data.get("board_id")
        class_id = data.get("class_id")
        institute_id = data.get("institute_id")
        academic_year = data.get("academic_year")
        subject_ids = data.get("subject_ids", None)

        #  Required Validation
        if board_id is None or class_id is None or institute_id is None or academic_year is None:
            return api_response(
                message="board_id, class_id, institute_id and academic_year are required",
                code=400,
                status="error"
            )

        # if not isinstance(subject_ids, list) or len(subject_ids) == 0:
        #     return api_response(
        #         message="subject_ids must be a non-empty list",
        #         code=400,
        #         status="error"
        #     )

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            CALL master.sp_insert_board_class_user_mapping(
                %s,%s,%s,%s,%s,%s,
                NULL,NULL
            )
        """, (
            user_id,
            board_id,
            class_id,
            institute_id,
            academic_year,
            subject_ids
        ))

        result = cur.fetchone()
        conn.commit()

        if not result:
            return api_response(
                message="Subscription process failed",
                code=500,
                status="error"
            )

        if result["p_status"] != "success":
            return api_response(
                message=result["p_message"],
                code=400,
                status="error"
            )

        return api_response(
            message=result["p_message"],
            code=200,
            status="success",
            data={
                "user_id": user_id,
                "board_id": board_id,
                "class_id": class_id,
                "academic_year": academic_year
            }
        )

    except Exception as e:
        if conn:
            conn.rollback()

        return api_response(
            message="Internal Server Error",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if conn:
            conn.close()
