import csv
import io
import json
import psycopg2.extras
import openpyxl 
from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response

def bulk_upload_teachers():
    """ 
    POST /api/v1/institute_admin/teachers/bulk_upload 
    Content-Type: multipart/form-data
    """
    conn = None
    cur = None
    try:
        # 1. Get User ID from token
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str: 
            return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
        admin_user_id = int(user_id_str)
        
        # 2. Open DB Connection EARLY to fetch Institute ID
        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 3. Try to get Institute ID from token first
        payload = TokenVerifier.get_user_payload()
        institute_id = payload.get('institute_id') 

        # [NEW LOGIC]: If not in token, fetch it from the database!
        if not institute_id:
            cur.execute("""
                SELECT institute_id 
                FROM login.user_role_mapping 
                WHERE user_id = %s AND institute_id IS NOT NULL 
                LIMIT 1
            """, (admin_user_id,))
            
            row = cur.fetchone()
            if row and row.get('institute_id'):
                institute_id = row['institute_id']
            else:
                return api_response(message="Institute ID not found for this admin in the database.", code=403, status="error")

        # 4. Check File Upload
        if 'file' not in request.files:
            return api_response(message="No file uploaded.", code=400, status="error")
            
        file = request.files['file']
        if file.filename == '':
            return api_response(message="Empty file", code=400, status="error")

        filename = file.filename.lower()
        teachers_list = []

        # 5. Parse File
        try:
            if filename.endswith('.csv'):
                stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
                reader = csv.DictReader(stream)
                
                if reader.fieldnames:
                    reader.fieldnames = [str(col).strip().lower() for col in reader.fieldnames]
                else:
                    return api_response(message="CSV file is empty or missing headers.", code=400, status="error")

                if not all(col in reader.fieldnames for col in ['name', 'email', 'mobile']):
                    return api_response(message="Missing required columns: name, email, mobile", code=400, status="error")

                for row in reader:
                    name = str(row.get('name', '')).strip()
                    email = str(row.get('email', '')).strip()
                    mobile = str(row.get('mobile', '')).strip()
                    
                    if name and email and mobile:
                        teachers_list.append({"name": name, "email": email, "mobile": mobile})

            elif filename.endswith(('.xls', '.xlsx')):
                wb = openpyxl.load_workbook(file, data_only=True)
                sheet = wb.active
                rows = list(sheet.iter_rows(values_only=True))

                if len(rows) < 2:
                    return api_response(message="Excel file is empty.", code=400, status="error")

                headers = [str(h).strip().lower() if h else '' for h in rows[0]]
                
                try:
                    name_idx = headers.index('name')
                    email_idx = headers.index('email')
                    mobile_idx = headers.index('mobile')
                except ValueError:
                    return api_response(message="Missing required columns: name, email, mobile", code=400, status="error")

                for row in rows[1:]:
                    name = str(row[name_idx] if row[name_idx] is not None else '').strip()
                    email = str(row[email_idx] if row[email_idx] is not None else '').strip()
                    mobile_raw = row[mobile_idx]

                    if isinstance(mobile_raw, float):
                        mobile = str(int(mobile_raw))
                    else:
                        mobile = str(mobile_raw if mobile_raw is not None else '').strip()

                    if name and email and mobile:
                        teachers_list.append({"name": name, "email": email, "mobile": mobile})

            else:
                return api_response(message="Invalid format. Use .csv or .xlsx", code=400, status="error")

        except Exception as e:
            return api_response(message="Error reading file contents.", code=400, status="error", error=str(e))

        if not teachers_list:
            return api_response(message="No valid rows found. Name, Email, and Mobile are all mandatory.", code=400, status="error")

        # 6. Execute Stored Procedure
        cur.execute("""
            CALL common.usp_institute_bulk_upload_teachers(
                %s, %s, %s::jsonb, 
                NULL, NULL, NULL, NULL
            )
        """, (admin_user_id, institute_id, json.dumps(teachers_list)))
        
        result = cur.fetchone()

        if result and result.get('o_status_code') == 200:
            added = result.get('o_added_count', 0)
            skipped = result.get('o_skipped_count', 0)
            return api_response(
                message=f"Upload complete! {added} new teachers added. {skipped} existing skipped.", 
                code=200, 
                status="success", 
                data={"added_count": added, "skipped_count": skipped}
            )

        return api_response(message=result.get('o_message'), code=result.get('o_status_code', 400), status="error")

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))
    finally:
        # Safely close connections
        if cur: cur.close()
        if conn: conn.close()