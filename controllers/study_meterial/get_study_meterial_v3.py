from flask import request
import jwt
from config import JWT_SECRET, get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier


def sp_get_study_material_v3():
    try:
        # =========================
        # ✅ TOKEN VERIFY (BEST PRACTICE)
        # =========================
        user_id, subscription_id, error = TokenVerifier.verify_admin_tokens()

        if error:
            return api_response(message=error, code=401, status="error")

        # =========================
        # ✅ DB CALL
        # =========================
        conn = get_db_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        cursor.execute("BEGIN")

        # 🔥 UPDATED SP CALL (USER + SUBSCRIPTION BASED)
        cursor.execute(
            "CALL learning.sp_get_study_material_v3(%s, %s, %s)",
            (user_id, subscription_id, "cur1")
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
                    "chapter_id": row[9],
                    "chapter_name": row[10],
                    "subject_id": row[11],  
                    "subject_name": row[12],
                    "section_name": row[13],
                    "description": row[14],
                }

            # 🔥 RESOURCE HANDLING
            item["resource"] = (
                item["link_url"]
                if item["file_type"] == "link"
                else item["file_url"]
            )

            data.append(item)

        conn.commit()
        cursor.close()
        conn.close()

        return api_response(
            message="Study material fetched successfully",
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
