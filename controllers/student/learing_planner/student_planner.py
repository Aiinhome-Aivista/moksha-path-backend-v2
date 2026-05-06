            
import psycopg2
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils import api_response
from flask import request
import jwt


# student learing planner  

def get_student_planner_dashboard():
    conn = None
    try:
        # 🔐 USER ID
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error")

        user_id = int(user_id_str)

        # 🔐 SUB TOKEN
        sub_token = request.headers.get('Subscription-Token')
        if not sub_token:
            return api_response(message="Subscription token missing", code=400, status="error")

        if "Bearer " in sub_token:
            sub_token = sub_token.split(" ")[1]

        # 🔥 DECODE TOKEN
        sub_payload = jwt.decode(sub_token, options={"verify_signature": False})

        subscription_id = sub_payload.get("sub_id")

        if not subscription_id:
            return api_response(message="Invalid subscription token", code=400, status="error")

        # 🛢 DB CALL
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            "CALL public.usp2_get_student_dashboard(%s,%s,NULL)",
            (user_id, subscription_id)
        )

        result = cur.fetchone()

        return api_response(
            message="Student Dashboard Loaded",
            code=200,
            status="success",
            data=result.get("p_result")
        )

    except Exception as e:
        return api_response(
            message="Error",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if conn:
            conn.close()     
            

# multi chapter test 
            
def get_multi_chapter_tests():
    conn = None
    try:
        # 🔐 AUTH USER
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(
                message="Unauthorized",
                code=401,
                status="error",
                error=auth_error
            )

        user_id = int(user_id_str)

        # 🔐 GET SUB TOKEN
        sub_token = request.headers.get("Subscription-Token")

        if not sub_token:
            return api_response(
                message="Subscription token missing",
                code=400,
                status="error"
            )

        # ✅ remove Bearer
        if "Bearer " in sub_token:
            sub_token = sub_token.split(" ")[1]

        # ✅ DECODE TOKEN
        sub_payload = jwt.decode(sub_token, options={"verify_signature": False})

        subscription_code = sub_payload.get("sub_id") or sub_payload.get("subscription_id")

        if not subscription_code:
            return api_response(
                message="Invalid subscription token",
                code=400,
                status="error"
            )

        # =====================================================
        # 🛢 DB CALL (MULTI CHAPTER TEST LIST)
        # =====================================================
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            CALL public.usp_get_multi_chapter_tests(%s, %s, %s)
            """,
            (
                user_id,
                subscription_code,
                None  # OUT param placeholder
            )
        )

        #  FETCH RESPONSE
        # result = cur.fetchone()
        # data = result[0] if result and result[0] else []
        result = cur.fetchone()

        # print("RAW RESULT:", result)

        data = []
        if result and "p_result" in result and result["p_result"]:
            data = result["p_result"]
        return api_response(
            message="Multi chapter tests fetched successfully",
            code=200,
            status="success",
            data=data
        )

    except Exception as e:
        print("REAL ERROR:", repr(e))
        return api_response(
            message="Internal Server Error",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if conn:
            conn.close()  

 
def get_student_subjects_tab_info():
    conn = None
    try:
        user_id_str, _ = TokenVerifier.get_user_id()
        user_id = int(user_id_str)

        sub_token = request.headers.get("Subscription-Token")
        if "Bearer " in sub_token:
            sub_token = sub_token.split(" ")[1]

        sub_payload = jwt.decode(sub_token, options={"verify_signature": False})
        subscription_id = sub_payload.get("sub_id")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            CALL public.usp_v1_get_student_subjects_tab_info(%s, %s, %s)
        """, (user_id, subscription_id, None))

        row = cur.fetchone()

        return api_response(
            message="Subjects fetched",
            data=row.get("p_result"),
            status="success"
        )

    except Exception as e:
        return api_response(
            message="Error",
            error=str(e),
            status="error"
        )

    finally:
        if conn:
            conn.close() 
            
        
def get_student_dashboard_view():
    conn = None
    try:
        # 🔐 USER ID
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error")

        user_id = int(user_id_str)

        # 🛢 DB CONNECT
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 🔥 VIEW CALL (only this)
        cur.execute("""
            SELECT *
            FROM report.student_kpi_setwise_final
            WHERE user_id  = %s
            ORDER BY set_id ASC
        """, (user_id,))

        result = cur.fetchall()

        return api_response(
            message="Student Dashboard Loaded",
            code=200,
            status="success",
            data=result
        )

    except Exception as e:
        return api_response(
            message="Error",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if conn:
            conn.close()                      
            
