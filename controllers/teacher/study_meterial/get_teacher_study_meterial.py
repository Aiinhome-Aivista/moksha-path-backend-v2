from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
from utils.youtube_thumbnail import get_youtube_thumbnail


def get_teacher_study_material():
    try:
        # =========================
        # ✅ TOKEN VERIFY
        # =========================
        teacher_id, _, error = TokenVerifier.verify_admin_tokens()

        if error:
            return api_response(message=error, code=401, status="error")

        # =========================
        # ✅ REQUEST PARSE
        # =========================
        if request.is_json:
            req = request.get_json()
        else:
            req = request.form

        def parse_array(value):
            if not value:
                return None
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                return [int(x) for x in value.split(",") if x.strip()]
            return None

        class_ids = parse_array(req.get("class_ids"))
        subject_ids = parse_array(req.get("subject_ids"))
        section_ids = parse_array(req.get("section_ids"))

        # =========================
        # ✅ DB CALL
        # =========================
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("BEGIN")

        cursor.execute(
            "CALL learning.sp_get_teacher_study_material(%s, %s, %s, %s, %s)",
            (teacher_id, class_ids, subject_ids, section_ids, "cur1"),
        )

        cursor.execute("FETCH ALL FROM cur1")
        rows = cursor.fetchall()

        conn.commit()

        # =========================
        # ✅ BUILD RESPONSE
        # =========================
        data = []

        # 🔥 FILTER SET (unique values)
        class_set = set()
        subject_map = {}
        section_map = {}
        chapter_map = {}
        board_map = {}
        thumbnail_cache = {}

        for row in rows:
            link_url = row["link_url"]

            # ---------- THUMBNAIL (CACHED) ----------
            thumbnail = None

            if row["file_type"] == "link" and link_url:
                if link_url in thumbnail_cache:
                    thumbnail = thumbnail_cache[link_url]
                else:
                    thumbnail = get_youtube_thumbnail(link_url)
                    thumbnail_cache[link_url] = thumbnail

            # ---------- MAIN DATA ----------
            item = {
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "class_id": row["class_id"],
                "subject_id": row["subject_id"],
                "chapter_id": row["chapter_id"],
                "section_id": row["section_id"],
                "file_type": row["file_type"],

                "resource": (
                    link_url if row["file_type"] == "link" else row["file_url"]
                ),

                # 🔥 NEW FIELD
                "thumbnail": thumbnail
            }

            data.append(item)

            # ---------- FILTER BUILD ----------
            class_set.add(row["class_id"])
            subject_map[row["subject_id"]] = row["subject_name"]
            section_map[row["section_id"]] = f"Section {row['section_id']}"

            chapter_map[row["chapter_id"]] = {
                "name": row["chapter_name"],
                "subject_id": row["subject_id"],
            }

            board_map[row["board_id"]] = row["board_name"]

        # =========================
        # ✅ FINAL FILTER STRUCTURE
        # =========================
        filters = {
            "boards": [{"id": bid, "name": bname} for bid, bname in board_map.items()],
            "classes": [{"id": cid, "name": f"Class {cid}"} for cid in class_set],
            "subjects": [
                {"id": sid, "name": sname} for sid, sname in subject_map.items()
            ],
            "sections": [
                {"id": sid, "name": name} for sid, name in section_map.items()
            ],
            "chapters": [
                {
                    "id": cid,
                    "name": cdata["name"],
                    "subject_id": cdata["subject_id"],
                }
                for cid, cdata in chapter_map.items()
            ],
            "file_types": ["study_material", "practice_material", "link"],
        }

        cursor.close()
        conn.close()

        return api_response(
            message="Teacher study material fetched successfully",
            data={
                "filters": filters,
                "data": data,
            },
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
