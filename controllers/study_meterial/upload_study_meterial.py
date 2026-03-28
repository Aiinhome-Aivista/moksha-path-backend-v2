# import os
# import uuid
# from flask import request
# import jwt
# from config import JWT_SECRET, get_db_connection
# from utils.api_response import api_response

# BASE_DIR = os.getcwd()
# UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "notes")

# os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# def to_int(value):
#     try:
#         return int(value) if value else None
#     except:
#         return None


# def upload_study_material():
#     try:
#         # =========================
#         # ✅ HEADERS
#         # =========================
#         auth_header = request.headers.get("Authorization")
#         sub_token = request.headers.get("subscription-token") or request.headers.get(
#             "Subscription-Token"
#         )

#         if not auth_header or not auth_header.startswith("Bearer "):
#             return api_response("Missing Authorization Token", 401, "error")

#         if not sub_token:
#             return api_response("Missing Subscription Token", 401, "error")

#         token = auth_header.split(" ")[1]

#         try:
#             payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
#             uploaded_by = payload.get("sub")
#         except jwt.ExpiredSignatureError:
#             return api_response("Token expired", 401, "error")
#         except jwt.InvalidTokenError:
#             return api_response("Invalid Token", 401, "error")

#         if not uploaded_by:
#             return api_response("Unauthorized", 401, "error")

#         # =========================
#         # ✅ FORM DATA
#         # =========================
#         title = request.form.get("title")
#         file_type = request.form.get("file_type")
#         link_url = request.form.get("link_url")

#         board_id = to_int(request.form.get("board_id"))
#         institute_id = to_int(request.form.get("institute_id"))
#         class_id = to_int(request.form.get("class_id"))
#         subject_id = to_int(request.form.get("subject_id"))
#         chapter_id = to_int(request.form.get("chapter_id"))
#         section_id = to_int(request.form.get("section_id"))

#         if file_type not in ["practice_material", "study_material", "link"]:
#             return api_response("Invalid file_type", 400, "error")

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         file_ids = []

#         # =========================
#         # 🟢 CASE 1: LINK
#         # =========================
#         if file_type == "link":

#             if not link_url:
#                 return api_response("Link URL is required", 400, "error")

#             if not title:
#                 title = "External Resource"

#             cursor.execute(
#                 """
#                 CALL learning.sp_upload_study_material(
#                     %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
#                 )
#             """,
#                 (
#                     board_id,
#                     institute_id,
#                     class_id,
#                     subject_id,
#                     chapter_id,
#                     section_id,
#                     title,
#                     file_type,
#                     None,
#                     None,
#                     link_url,
#                     uploaded_by,
#                     None,
#                 ),
#             )

#             result = cursor.fetchone()
#             if result:
#                 file_id = result.get("v_id") if isinstance(result, dict) else result[0]
#                 file_ids.append(file_id)

#         # =========================
#         # 🟢 CASE 2: FILE UPLOAD
#         # =========================
#         else:
#             if not title:
#                 return api_response("Title is required for file upload", 400, "error")

#             files = request.files.getlist("files")
#             if not files:
#                 single_file = request.files.get("file")
#                 if single_file:
#                     files = [single_file]

#             if not files:
#                 return api_response("File is required", 400, "error")

#             for file in files:
#                 if not file or file.filename == "":
#                     continue

#                 unique_name = f"{uuid.uuid4()}_{file.filename}"
#                 file_path = os.path.join(UPLOAD_FOLDER, unique_name)
#                 file.save(file_path)

#                 file_url = f"/uploads/notes/{unique_name}"

#                 cursor.execute(
#                     """
#                     CALL learning.sp_upload_study_material(
#                         %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
#                     )
#                 """,
#                     (
#                         board_id,
#                         institute_id,
#                         class_id,
#                         subject_id,
#                         chapter_id,
#                         section_id,
#                         title,
#                         file_type,
#                         file.filename,
#                         file_url,
#                         None,
#                         uploaded_by,
#                         None,
#                     ),
#                 )

#                 result = cursor.fetchone()
#                 if result:
#                     file_id = (
#                         result.get("v_id") if isinstance(result, dict) else result[0]
#                     )
#                     file_ids.append(file_id)

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return api_response(
#             message="Uploaded successfully",
#             data={"file_ids": file_ids},
#             code=200,
#             status="success",
#         )

#     except Exception as e:
#         import traceback

#         return api_response(
#             message=str(e),
#             data={"trace": traceback.format_exc()},
#             code=500,
#             status="error",
#         )


import os
import uuid
from flask import request, send_from_directory
import jwt
from config import JWT_SECRET, get_db_connection
from utils.api_response import api_response

BASE_DIR = os.getcwd()
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "notes")
BASE_URL = "http://127.0.0.1:8000"  # change in production

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# ✅ FILE SERVE ROUTE
# =========================
def register_routes(app):
    @app.route('/uploads/notes/<path:filename>')
    def serve_notes(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)


# =========================
# ✅ UTILITY
# =========================
def to_int(value):
    try:
        return int(value) if value else None
    except:
        return None


# =========================
# ✅ MAIN API
# =========================
def upload_study_material():
    try:
        # =========================
        # 🔐 AUTH
        # =========================
        auth_header = request.headers.get("Authorization")
        sub_token = request.headers.get("subscription-token") or request.headers.get(
            "Subscription-Token"
        )

        if not auth_header or not auth_header.startswith("Bearer "):
            return api_response("Missing Authorization Token", 401, "error")

        if not sub_token:
            return api_response("Missing Subscription Token", 401, "error")

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            uploaded_by = payload.get("sub")
        except jwt.ExpiredSignatureError:
            return api_response("Token expired", 401, "error")
        except jwt.InvalidTokenError:
            return api_response("Invalid Token", 401, "error")

        if not uploaded_by:
            return api_response("Unauthorized", 401, "error")

        # =========================
        # 📥 FORM DATA
        # =========================
        title = request.form.get("title")
        file_type = request.form.get("file_type")
        link_url = request.form.get("link_url")

        board_id = to_int(request.form.get("board_id"))
        institute_id = to_int(request.form.get("institute_id"))
        class_id = to_int(request.form.get("class_id"))
        subject_id = to_int(request.form.get("subject_id"))
        chapter_id = to_int(request.form.get("chapter_id"))
        section_id = to_int(request.form.get("section_id"))

        if file_type not in ["practice_material", "study_material", "link"]:
            return api_response("Invalid file_type", 400, "error")

        conn = get_db_connection()
        cursor = conn.cursor()

        file_ids = []

        # =========================
        # 🟢 CASE 1: LINK
        # =========================
        if file_type == "link":
            if not link_url:
                return api_response("Link URL is required", 400, "error")

            if not title:
                title = "External Resource"

            cursor.execute(
                """
                CALL learning.sp_upload_study_material(
                    %s::int,
                    %s::int,
                    %s::int,
                    %s::int,
                    %s::int,
                    %s::int,
                    %s::text,
                    %s::text,
                    %s::text,
                    %s::text,
                    %s::text,
                    %s::int,
                    NULL
                )
                """,
                (
                    board_id,
                    institute_id,
                    class_id,
                    subject_id,
                    chapter_id,
                    section_id,
                    title,
                    file_type,
                    None,        # file_name
                    None,        # file_url
                    link_url,
                    uploaded_by,
                ),
            )

        # =========================
        # 🟢 CASE 2: FILE UPLOAD
        # =========================
        else:
            if not title:
                return api_response("Title is required for file upload", 400, "error")

            files = request.files.getlist("files")

            if not files:
                single_file = request.files.get("file")
                if single_file:
                    files = [single_file]

            if not files:
                return api_response("File is required", 400, "error")

            for file in files:
                if not file or file.filename == "":
                    continue

                unique_name = f"{uuid.uuid4()}_{file.filename}"
                file_path = os.path.join(UPLOAD_FOLDER, unique_name)
                file.save(file_path)

                # ✅ FULL URL
                file_url = f"{BASE_URL}/uploads/notes/{unique_name}"

                cursor.execute(
                """
                CALL learning.sp_upload_study_material(
                    %s::int,
                    %s::int,
                    %s::int,
                    %s::int,
                    %s::int,
                    %s::int,
                    %s::text,
                    %s::text,
                    %s::text,
                    %s::text,
                    %s::text,
                    %s::int,
                    NULL
                )
                """,
                (
                    board_id,
                    institute_id,
                    class_id,
                    subject_id,
                    chapter_id,
                    section_id,
                    title,
                    file_type,
                    file.filename,
                    file_url,
                    None,
                    uploaded_by,
                ),
    )

        conn.commit()
        cursor.close()
        conn.close()

        return api_response(
            message="Uploaded successfully",
            data={"message": "File uploaded and ready to access"},
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