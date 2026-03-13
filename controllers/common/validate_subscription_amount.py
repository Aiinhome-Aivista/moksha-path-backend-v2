from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier


def validate_subscription_amount():
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

        # ============================================
        # GET REQUEST DATA
        # ============================================
        data = request.get_json() or {}

        plan_id = data.get("plan_id")
        board_id = data.get("board_id")
        class_id = data.get("class_id")
        # subject_ids = data.get("subject_ids")
        
        subject_ids = [int(x) for x in data.get("subject_ids", [])]
        ui_total_amount = data.get("ui_total_amount")
        total_licences = data.get("total_licences")
        
        # [NEW] Optional Coupon Code (Defaults to None if not sent by UI)
        coupon_code = data.get("coupon_code") 


        # ============================================
        # BASIC VALIDATION
        # ============================================
        if not all([plan_id, board_id, class_id]) or ui_total_amount is None:
            return api_response(
                message="Required fields missing",
                code=400,
                status="error"
            )

        if not isinstance(subject_ids, list) or len(subject_ids) == 0:
            return api_response(
                message="subject_ids must be a non-empty list",
                code=400,
                status="error"
            )

        # ============================================
        # DB CONNECTION
        # ============================================
        conn = get_db_connection()
        cur = conn.cursor()

        # ============================================
        # CALL VALIDATION SP (UPDATED TO V3)
        # ============================================
        cur.execute("""
            CALL subscription.usp_v3_validate_subscription_amount(
                %s,%s,%s,%s::int[],%s,%s,%s,NULL,NULL,NULL
            )
        """, (
            plan_id,
            board_id,
            class_id,
            subject_ids,
            ui_total_amount,
            total_licences,
            coupon_code # <--- Passed to DB (Can be None)
        ))

        result = cur.fetchone()

        if not result:
            return api_response(
                message="Validation failed",
                code=400,
                status="error"
            )

        # ============================================
        # CHECK RESULT
        # ============================================
        if result.get("p_status") != "success":
            return api_response(
                message=result.get("p_message"),
                code=400,
                status="error",
                data={
                    "db_amount": float(result.get("p_db_amount") or 0)
                }
            )

        # ============================================
        # SUCCESS RESPONSE
        # ============================================
        return api_response(
            message=result.get("p_message"),
            code=200,
            status="success",
            data={
                "verified_amount": float(result.get("p_db_amount") or 0)
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