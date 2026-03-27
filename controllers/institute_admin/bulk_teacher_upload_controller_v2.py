import json
import csv
from flask import request, jsonify
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response


def bulk_upload_users_controller_v2():
    try:
        # -------------------------
        # Token Verification
        # -------------------------
        admin_user_id, admin_subscription_id, token_error = (
            TokenVerifier.verify_admin_tokens()
        )
        if token_error:
            return api_response(message=token_error, code=401, status="error")

        # =========================================================
        # CASE 1: CSV FILE UPLOAD
        # =========================================================
        if "file" in request.files:
            file = request.files["file"]

            if file.filename == "":
                return jsonify({"status": "error", "message": "No file selected"}), 400

            data = []

            # Read CSV
            stream = file.stream.read().decode("utf-8").splitlines()
            csv_reader = csv.DictReader(stream)

            for row in csv_reader:
                data.append({
                    "full_name": row.get("full_name"),
                    "email": row.get("email"),
                    "phone": row.get("phone"),
                    "username": row.get("username"),
                    "role_id": int(row.get("role_id")) if row.get("role_id") else None,
                    "institute_id": int(row.get("institute_id")) if row.get("institute_id") else None,
                    "subscription_id": row.get("subscription_id"),
                    "board_id": int(row.get("board_id")) if row.get("board_id") else None,
                    "academic_year": row.get("academic_year"),
                    "class_id": row.get("class_id"),
                    "section_ids": row.get("section_ids"),
                    "subject_ids": row.get("subject_ids"),
                })

            p_data = data

        # =========================================================
        # CASE 2: JSON BODY
        # =========================================================
        else:
            req_data = request.get_json()

            if not req_data:
                return jsonify({
                    "status": "error",
                    "message": "Request body is required"
                }), 400

            if "data" not in req_data:
                return jsonify({
                    "status": "error",
                    "message": "data is required"
                }), 400

            p_data = req_data.get("data")

        # -------------------------
        # Final Validation
        # -------------------------
        if not isinstance(p_data, list) or len(p_data) == 0:
            return jsonify({
                "status": "error",
                "message": "data must be a non-empty array"
            }), 400

        # -------------------------
        # DB Call
        # -------------------------
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "CALL public.usp_bulk_upload_users(%s, %s)",
            (json.dumps(p_data), admin_user_id),
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Bulk users uploaded successfully",
            "total_records": len(p_data)
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500