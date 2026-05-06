
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
