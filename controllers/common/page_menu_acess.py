# import jwt
# import psycopg2.extras
# from flask import request
# from config import get_db_connection, JWT_SECRET
# from utils.api_response import api_response
# from utils.subscription_helper import get_active_subscription


# def get_user_menu():

#     conn = None

#     try:

#         # 1. Get Token
#         auth_header = request.headers.get('Authorization')

#         if not auth_header:
#             return api_response(
#                 message="Authorization header missing",
#                 code=401,
#                 status="error"
#             )

#         try:

#             token = auth_header.split(" ")[1]

#             payload = jwt.decode(
#                 token,
#                 JWT_SECRET,
#                 algorithms=["HS256"]
#             )

#         except jwt.ExpiredSignatureError:
#             return api_response(
#                 message="Token expired",
#                 code=401,
#                 status="error"
#             )

#         except jwt.InvalidTokenError:
#             return api_response(
#                 message="Invalid token",
#                 code=401,
#                 status="error"
#             )


#         # 2. Extract role_id and subscription_id

#         roles = payload.get("roles", [])
#         user_id = int(payload.get("sub"))

#         if not roles:
#             return api_response(
#                 message="No roles found",
#                 code=403,
#                 status="error"
#             )

#         role_id = roles[0]["role_id"]

#         # subscription_id = payload.get("sub_id")

#         # if not subscription_id:
#         #     return api_response(
#         #         message="Subscription not found in token",
#         #         code=403,
#         #         status="error"
#         #     )
#         #  Fetch active subscription from DB
#         subscription_id = get_active_subscription(user_id)
        
#         if not subscription_id:
#             return api_response(
#                 message="Active subscription not found",
#                 code=403,
#                 status="error"
#             )

#         # 3. Call Procedure

#         conn = get_db_connection()

#         conn.autocommit = True

#         cur = conn.cursor(
#             cursor_factory=psycopg2.extras.RealDictCursor
#         )


#         cur.execute(
#             """
#             CALL login.usp_v2_get_role_menu(
#                 %s,
#                 %s,
#                 NULL,
#                 NULL,
#                 NULL
#             )
#             """,
#             (role_id, subscription_id)
#         )

#         result = cur.fetchone()


#         return api_response(
#             message=result["p_message"],
#             code=result["p_status_code"],
#             data=result["p_menu_json"]
#         )


#     except Exception as e:

#         return api_response(
#             message=str(e),
#             code=500,
#             status="error"
#         )

#     finally:

#         if conn:
#             conn.close()

import psycopg2.extras
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier


def get_user_menu():

    conn = None

    try:

        #  Get Full Payload
        payload = TokenVerifier.get_user_payload()

        if not payload:
            return api_response(
                message="Invalid or expired token",
                code=401,
                status="error"
            )

        role_id = payload.get("role_id")

        if not role_id:
            return api_response(
                message="Role not found in token",
                code=403,
                status="error"
            )

        #  Call V3 Procedure

        conn = get_db_connection()
        conn.autocommit = True

        cur = conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )

        cur.execute(
            """
            CALL login.usp_v3_get_role_menu(
                %s,
                NULL,
                NULL,
                NULL
            )
            """,
            (role_id,)
        )

        result = cur.fetchone()

        return api_response(
            message=result["p_message"],
            code=result["p_status_code"],
            data=result["p_menu_json"]
        )

    except Exception as e:
        return api_response(
            message=str(e),
            code=500,
            status="error"
        )

    finally:
        if conn:
            conn.close()
