from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras
import json


def log_user_activity():

    conn = None

    try:

        # AUTH
        user_id_str, auth_error = TokenVerifier.get_user_id()

        if not user_id_str:
            return api_response(
                message="Unauthorized", code=401, status="error", error=auth_error
            )

        # INPUT
        data = request.get_json() or {}

        event_name = data.get("event_name")

        event_data = data.get("event_data")

        if not event_name:
            return api_response(
                message="event_name is required", code=400, status="error"
            )

        # DB CALL
        conn = get_db_connection()

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            """

            CALL analytics.usp_v1_insert_user_event(

                %s,
                %s,
                %s::jsonb,

                NULL,
                NULL,
                NULL

            )

        """,
            (user_id_str, event_name, json.dumps(event_data)),
        )

        result = cur.fetchone()

        # RESPONSE
        return api_response(
            message=result.get("p_message"),
            code=200 if result.get("p_status") == "success" else 400,
            status=result.get("p_status"),
            data=result.get("p_data"),
        )

    except Exception as e:

        return api_response(
            message="Internal Server Error", code=500, status="error", error=str(e)
        )

    finally:

        if conn:
            conn.close()
