from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras
import jwt

def create_subject_wise_adaptive_assessment():
    conn = None
    try:
        # AUTH
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)

        user_id = int(user_id_str)

        # SUB TOKEN
        sub_token = request.headers.get('Subscription-Token')
        sub_payload = jwt.decode(sub_token, options={"verify_signature": False})
        subscription_id = sub_payload.get('sub_id') or sub_payload.get('subscription_id')

        # INPUT
        data = request.get_json()

        subject_id = data.get("subject_id")
        chapters_array = data.get("chapters_array")
        student_ids = data.get("student_ids")
        total_questions = data.get("total_questions")
        total_marks = data.get("total_marks")
        duration = data.get("duration")

        if not subject_id or not chapters_array:
            return api_response(message="subject_id and chapters_array required", code=400, status="error")

        # DB CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            CALL learning.usp_create_subject_wise_adaptive_assessment_v2(
                %s,%s,%s,%s,%s,%s,%s,%s,
                NULL,NULL,NULL
            )
        """, (
            user_id,
            subscription_id,
            subject_id,
            chapters_array,
            student_ids,
            total_questions,
            total_marks,
            duration
        ))

        # result = cur.fetchone()
        # conn.commit()

        # return api_response(
        #     message=result.get("p_message"),
        #     data=result.get("p_data"),
        #     code=200,
        #     status="success"
        # )
        result = cur.fetchone()

        res_data = result.get("p_data") or {}

        #  STEP 1: set_id fetch
        # new_set_id = res_data.get("set_id")

        #  STEP 2: slot generation call
        # if new_set_id:
        #     cur.execute(
        #         "CALL learning.usp_generate_question_slots(%s::BIGINT)",
        #         (new_set_id,)
        #     )
        set_ids = res_data.get("set_ids") or []

        for sid in set_ids:
            cur.execute(
                "CALL learning.usp_generate_question_slots(%s::BIGINT)",
                (sid,)
            )

        #  STEP 3: commit AFTER slot generation
        conn.commit()

        return api_response(
            message=result.get("p_message"),
            data=res_data,
            code=200,
            status="success"
        )
    except Exception as e:
        if conn: conn.rollback()
        return api_response(message="Error", code=500, status="error", error=str(e))

    finally:
        if conn:
            conn.close()