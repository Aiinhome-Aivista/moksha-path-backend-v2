from flask import request
import jwt
from config import JWT_SECRET, get_db_connection
from utils.api_response import api_response


def get_study_material():
    try:
        # =========================
        # ✅ HEADERS
        # =========================
        auth_header = request.headers.get("Authorization")
        sub_token = request.headers.get("Subscription-Token") or request.headers.get("subscription-token")

        if not auth_header or not auth_header.startswith("Bearer "):
            return api_response("Missing Authorization Token", 401, "error")

        if not sub_token:
            return api_response("Missing Subscription Token", 401, "error")

        token = auth_header.split(" ")[1]

        try:
            jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            jwt.decode(sub_token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return api_response("Token expired", 401, "error")
        except Exception:
            return api_response("Invalid Token", 401, "error")

        # =========================
        # ✅ DB CALL
        # =========================
        conn = get_db_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        cursor.execute("BEGIN")

        cursor.execute(
            "CALL learning.sp_get_study_material(%s)",
            ("cur1",)
        )

        cursor.execute("FETCH ALL FROM cur1")
        rows = cursor.fetchall()

        data = []

        for row in rows:
            if isinstance(row, dict):
                item = row
            else:
                item = {
                    "id": row[0],
                    "title": row[1],
                    "file_type": row[2],
                    "file_name": row[3],
                    "file_url": row[4],
                    "link_url": row[5],
                    "section_id": row[6],
                    "uploaded_by": row[7],
                    "uploaded_at": str(row[8]),
                }

            # 🔥 smart response formatting
            if item["file_type"] == "link":
                item["resource"] = item["link_url"]
            else:
                item["resource"] = item["file_url"]

            data.append(item)

        conn.commit()
        cursor.close()
        conn.close()

        return api_response(
            message="Files fetched successfully",
            data=data,
            code=200,
            status="success",
        )

    except Exception as e:
        import traceback
        return api_response(
            message=str(e),
            data={"trace": traceback.format_exc()},
            code=500,
            status="error",
        )