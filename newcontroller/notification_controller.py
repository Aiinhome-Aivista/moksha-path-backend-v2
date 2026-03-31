from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras
from firebase_admin import messaging


# SAVE USER FCM TOKEN

def save_token_controller():

    conn = None

    try:

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

        token = data.get("token")

        if not token:

            return api_response(
                message="Token missing",
                code=400,
                status="error"
            )

        conn = get_db_connection()

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            """
            CALL common.sp_save_user_fcm_token(
                %s,
                %s,
                NULL,
                NULL,
                NULL
            )
            """,
            (user_id, token)
        )

        result = cur.fetchone()

        if not result:

            return api_response(
                message="Failed to save token",
                code=500,
                status="error"
            )

        return api_response(
            message=result.get("p_message"),
            code=200 if result.get("p_status") == "success" else 500,
            status=result.get("p_status"),
            data=result.get("p_data")
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


# SEND NOTIFICATIONS TO ASSIGNED STUDENTS

def send_notification_to_assigned_students_controller():

    conn = None

    try:

        # Extract teacher_id from token
        user_id_str, auth_error = TokenVerifier.get_user_id()

        if not user_id_str:

            return api_response(
                message="Unauthorized",
                code=401,
                status="error",
                error=auth_error
            )

        teacher_id = int(user_id_str)


        data = request.get_json() or {}

        class_id = data.get("class_id")
        subject_id = data.get("subject_id")
        section = str(data.get("section"))


        if not class_id or not subject_id or not section:

            return api_response(
                message="class_id, subject_id and section required",
                code=400,
                status="error"
            )


        conn = get_db_connection()

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            """
            CALL common.sp_get_assigned_students_tokens(
                %s,
                %s,
                %s,
                %s,
                NULL,
                NULL,
                NULL
            )
            """,
            (teacher_id, class_id, subject_id, section)
        )


        result = cur.fetchone()


        if not result:

            return api_response(
                message="Failed to fetch student tokens",
                code=500,
                status="error"
            )


        if result.get("p_status") != "success":

            return api_response(
                message=result.get("p_message"),
                code=500,
                status="error"
            )

        sp_data = result.get("p_data") or {}

        total_students = sp_data.get("total_students", 0)

        tokens = [

            token_obj.get("token")

            for token_obj in sp_data.get("tokens", [])

            if token_obj.get("token")

        ]

        if not tokens:

            return api_response(
                message="No tokens found",
                code=200,
                status="success",
                data={
                    "total_students": total_students,
                    "total_notifications_sent": 0
                }
            )

        # SEND FIREBASE PUSH NOTIFICATIONS

        success_count = 0

        for token in tokens:

            try:

                message = messaging.Message(

                    notification=messaging.Notification(
                        title="New Test Assigned 📘",
                        body="Your teacher has assigned a new test."
                    ),

                    token=token

                )

                messaging.send(message)

                success_count += 1

            except Exception as firebase_error:

                print("Firebase Error:", firebase_error)


        return api_response(
            message="Notification sent successfully",
            code=200,
            status="success",
            data={
                "total_students": total_students,
                "total_notifications_sent": success_count
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