# import jwt
# import datetime
# import psycopg2.extras
# from flask import request

# from config import get_db_connection, JWT_SECRET
# from utils.api_response import api_response
# from utils.token_helper import TokenVerifier

# def complete_subscription():
#     conn = None
#     try:
#         # ================= AUTH =================
#         user_id_str, auth_error = TokenVerifier.get_user_id()
#         if not user_id_str:
#             return api_response(
#                 message="Unauthorized",
#                 code=401,
#                 status="error",
#                 error=auth_error
#             )

#         user_id = int(user_id_str)
        
#         # Grab current token payload to carry over roles to the new sub token
#         token_payload = TokenVerifier.get_user_payload() or {}
#         role_id = token_payload.get('role_id')
#         roles = token_payload.get('roles', [])

#         data = request.get_json() or {}
#         plan_id = data.get("plan_id")
#         board_id = data.get("board_id")
#         class_id = data.get("class_id")
#         institute_id = data.get("institute_id")
#         subject_ids = data.get("subject_ids")
#         total_licenses = data.get("total_licenses")
#         licenses_used = data.get("licenses_used")
#         transaction_id = data.get("transaction_id")
#         subscription_name = data.get("subscription_name")
#         ui_total_amount = data.get("ui_total_amount")
        
#         # Optional Coupon Code
#         coupon_code = data.get("coupon_code")

#         # ================= VALIDATION =================
#         if not all([plan_id, board_id, class_id, transaction_id]):
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

#         try:
#             plan_id = int(plan_id)
#             board_id = int(board_id)
#             class_id = int(class_id)
#             institute_id = int(institute_id) if institute_id else None
#             total_licenses = int(total_licenses or 0)
#             licenses_used = int(licenses_used or 0)
#             ui_total_amount = float(ui_total_amount) if ui_total_amount is not None else None
#         except ValueError:
#             return api_response(
#                 message="Invalid numeric values",
#                 code=400,
#                 status="error"
#             )

#         # ================= DB CALL =================
#         conn = get_db_connection()
#         conn.autocommit = True 
        
#         # MUST use RealDictCursor for result.get() to work!
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         # Call V3 Procedure
#         cur.execute("""
#         CALL subscription.usp_v3_complete_subscription(
#             %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
#             %s, 
#             NULL, -- p_subscription_code (OUT)
#             NULL, -- p_status (OUT)
#             NULL  -- p_message (OUT)
#         )
#         """, (
#             user_id, plan_id, board_id, class_id, institute_id, 
#             subject_ids, total_licenses, licenses_used, transaction_id, 
#             subscription_name, ui_total_amount, coupon_code
#         ))

#         result = cur.fetchone()
        
#         if not result:
#             return api_response(
#                 message="Subscription completion failed",
#                 code=400,
#                 status="error"
#             )

#         if result.get("p_status") != "success":
#             return api_response(
#                 message=result.get("p_message"),
#                 code=400,
#                 status="error"
#             )

#         # ================= GENERATE NEW SUBSCRIPTION TOKEN =================
#         # Extract the newly generated subscription code from the SP output
#         new_sub_id = result.get("p_subscription_code") or result.get("p_subscription_id")
#         sub_token = None

#         if new_sub_id:
#             exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
#             sub_payload = {
#                 "sub": str(user_id),
#                 "role_id": role_id,
#                 "roles": roles,
#                 "sub_id": new_sub_id,
#                 "subscription_id": new_sub_id,
#                 "exp": int(exp_time.timestamp())
#             }
#             sub_token = jwt.encode(sub_payload, JWT_SECRET, algorithm="HS256")

#         return api_response(
#             message=result.get("p_message"),
#             code=200,
#             status="success",
#             data={
#                 "subscription_id": new_sub_id,
#                 "subscription_token": sub_token  # Returned specifically so UI can update context instantly
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
#             cur.close()
#             conn.close()


import jwt
import datetime
import psycopg2.extras
from flask import request

from config import get_db_connection, JWT_SECRET
from utils.api_response import api_response
from utils.token_helper import TokenVerifier


def complete_subscription():
    conn = None
    cur = None

    try:
        # ================= AUTH =================
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(
                message="Unauthorized",
                code=401,
                status="error",
                error=auth_error
            )

        user_id = int(user_id_str)

        # get role info (for token regeneration)
        token_payload = TokenVerifier.get_user_payload() or {}
        role_id = token_payload.get("role_id")
        roles = token_payload.get("roles", [])

        # ================= REQUEST =================
        data = request.get_json() or {}

        profiles = data.get("profiles")
        transaction_id = data.get("transaction_id")
        subscription_name = data.get("subscription_name")

        db_total = data.get("db_total")
        db_discount = data.get("db_discount")
        db_final = data.get("db_final")

        coupon_code = data.get("coupon_code")
        currency = data.get("currency", "INR")

        # ================= BASIC VALIDATION =================
        if not profiles or not isinstance(profiles, list):
            return api_response(
                message="profiles required",
                code=400,
                status="error"
            )

        if not transaction_id:
            return api_response(
                message="transaction_id required",
                code=400,
                status="error"
            )

        try:
            db_total = float(db_total or 0)
            db_discount = float(db_discount or 0)
            db_final = float(db_final or 0)
        except ValueError:
            return api_response(
                message="Invalid amount values",
                code=400,
                status="error"
            )

        # ================= DB =================
        conn = get_db_connection()
        conn.autocommit = True

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # ================= CALL SP =================
        cur.execute("""
            CALL subscription.usp_v3_complete_subscription_bulk(
                %s, %s::jsonb, %s, %s,
                %s, %s, %s,
                %s, %s,
                NULL, NULL, NULL
            )
        """, (
            user_id,
            psycopg2.extras.Json(profiles),
            transaction_id,
            subscription_name,
            db_total,
            db_discount,
            db_final,
            coupon_code,
            currency
        ))

        result = cur.fetchone()

        if not result:
            return api_response(
                message="Subscription failed",
                code=400,
                status="error"
            )

        if result.get("p_status") != "success":
            return api_response(
                message=result.get("p_message"),
                code=400,
                status="error"
            )

        # ================= TOKEN GENERATION =================
        sub_id = result.get("p_subscription_code")

        sub_token = None
        if sub_id:
            exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)

            payload = {
                "sub": str(user_id),
                "role_id": role_id,
                "roles": roles,
                "subscription_id": sub_id,
                "sub_id": sub_id,
                "exp": int(exp_time.timestamp())
            }

            sub_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

        # ================= SUCCESS =================
        return api_response(
            message=result.get("p_message"),
            code=200,
            status="success",
            data={
                "subscription_code": sub_id,
                "subscription_token": sub_token,
                "amount": {
                    "total": db_total,
                    "discount": db_discount,
                    "final": db_final,
                    "currency": currency
                }
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
        if cur:
            cur.close()
        if conn:
            conn.close()





