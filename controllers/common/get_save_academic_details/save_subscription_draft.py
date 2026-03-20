# from flask import request
# from config import get_db_connection
# from utils.api_response import api_response
# from utils.token_helper import TokenVerifier


# def save_subscription_draft():
#     conn = None
#     try:
#         # ============================================
#         # AUTH CHECK
#         # ============================================
#         user_id_str, auth_error = TokenVerifier.get_user_id()
#         if not user_id_str:
#             return api_response(
#                 message="Unauthorized",
#                 code=401,
#                 status="error",
#                 error=auth_error
#             )

#         user_id = int(user_id_str)
#         data = request.get_json() or {}

#         # ============================================
#         # GET REQUEST DATA
#         # ============================================
#         plan_id = data.get("plan_id")
#         board_id = data.get("board_id")
#         class_id = data.get("class_id")
#         institute_id = data.get("institute_id")
#         subject_ids = data.get("subject_ids")
#         total_licences = data.get("total_licences")
#         licences_used = data.get("licences_used")
#         subscription_name = data.get("subscription_name")


#         # ============================================
#         # BASIC VALIDATION
#         # ============================================
#         if not all([plan_id, board_id, class_id]):
#             return api_response(
#                 message="Required fields missing",
#                 code=400,
#                 status="error"
#             )

#         if not isinstance(subject_ids, list) or len(subject_ids) == 0:
#             return api_response(
#                 message="subject_ids must be a non-empty list",
#                 code=400,
#                 status="error"
#             )

#         # Optional numeric safety
#         total_licences = int(total_licences or 0)
#         licences_used = int(licences_used or 0)

#         # ============================================
#         # DB CONNECTION
#         # ============================================
#         conn = get_db_connection()
#         cur = conn.cursor()

#         # ============================================
#         # CALL DRAFT SAVE PROCEDURE
#         # ============================================
        
#         cur.execute("""
#             CALL subscription.usp_v2_save_subscription_draft(
#                 %s,%s,%s,%s,%s,%s,%s,%s,%s,
#                 NULL::INTEGER,
#                 NULL::VARCHAR,
#                 NULL::VARCHAR
#             )
#         """, (
#             user_id,
#             plan_id,
#             board_id,
#             class_id,
#             institute_id,
#             subscription_name,
#             subject_ids,
#             total_licences,
#             licences_used
#         ))


#         result = cur.fetchone()

#         if not result:
#             return api_response(
#                 message="Draft save failed",
#                 code=400,
#                 status="error"
#             )

#         if result.get("p_status") != "success":
#             return api_response(
#                 message=result.get("p_message"),
#                 code=400,
#                 status="error"
#             )

#         # ============================================
#         # SUCCESS RESPONSE
#         # ============================================
#         return api_response(
#             message=result.get("p_message"),
#             code=200,
#             status="success",
#             data={
#                 "subscription_id": result.get("p_subscription_id")
#             }
#         )

#     except Exception as e:
#         return api_response(
#             message="Internal Server Error",
#             code=500,
#             status="error",
#             error=str(e)
#         )

#     finally:
#         if conn:
#             conn.close()




from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import json


def save_subscription_draft():
    conn = None
    try:
        # ============================================
        # AUTH CHECK
        # ============================================
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

        # ============================================
        # GET DATA (NEW STRUCTURE)
        # ============================================
        profiles = data.get("profiles", [])
        ui_total_amount = data.get("ui_total_amount")

        # ============================================
        # BASIC VALIDATION
        # ============================================
        if not profiles or not isinstance(profiles, list):
            return api_response(
                message="profiles must be a non-empty array",
                code=400,
                status="error"
            )

        # ============================================
        # DB CONNECTION
        # ============================================
        conn = get_db_connection()
        cur = conn.cursor()

        # ============================================
        # CALL NEW BULK DRAFT SP
        # ============================================
        cur.execute("""
                CALL subscription.usp_v3_save_subscription_draft_bulk(
                    %s,
                    %s::jsonb,
                    %s,
                    NULL,
                    NULL
                )
            """, (
                user_id,
                json.dumps(profiles),
                ui_total_amount   # only this amount needed
            ))

        result = cur.fetchone()

        if not result:
            return api_response(
                message="Draft save failed",
                code=400,
                status="error"
            )

        if result.get("p_status") != "success":
            return api_response(
                message=result.get("p_message"),
                code=400,
                status="error"
            )

        # ============================================
        # SUCCESS RESPONSE
        # ============================================
        return api_response(
            message=result.get("p_message"),
            code=200,
            status="success",
            data={
                "subscription_code": result.get("p_subscription_code")
            }
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