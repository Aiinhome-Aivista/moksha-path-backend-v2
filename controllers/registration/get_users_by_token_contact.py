from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras


# =========================================================
# GET API: Fetch Users by Token Contact
# =========================================================
def get_users_by_token_contact():

    conn = None
    cur = None

    try:

        # =====================================================
        # 1. Get FULL token payload (Correct Method)
        # =====================================================

        token_payload = TokenVerifier.get_user_payload()
        print(f"Token Payload: {token_payload}")  # Debugging line to check payload content
        if not token_payload:
            return api_response(
                message="Unauthorized",
                code=401,
                status="error"
            )


        # =====================================================
        # 2. Extract email & mobile from token
        # =====================================================
         
        email = token_payload.get("email")
        mobile = token_payload.get("mobile")

        # fallback if token uses different key
        if not mobile:
            mobile = token_payload.get("phone")

        if not email and not mobile:
            return api_response(
                message="Email or Mobile not found in token",
                code=400,
                status="error"
            )


        # =====================================================
        # 3. DB Connection
        # =====================================================

        conn = get_db_connection()

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


        # =====================================================
        # 4. Call Stored Procedure
        # =====================================================

        cur.execute(
            """
            CALL login.usp_v5_get_users_by_contact(
                %s,
                %s,
                NULL,
                NULL,
                NULL
            )
            """,
            (email, mobile)
        )


        result = cur.fetchone()


        # =====================================================
        # 5. Handle Response
        # =====================================================

        if not result:
            return api_response(
                message="No response from database",
                code=500,
                status="error"
            )


        if result['p_status'] == 'true':

            return api_response(
                message=result['p_message'],
                code=200,
                status="success",
                data=result['p_data']
            )

        else:

            return api_response(
                message=result['p_message'],
                code=404,
                status="error"
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