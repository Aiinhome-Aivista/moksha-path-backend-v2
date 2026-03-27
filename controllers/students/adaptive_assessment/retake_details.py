from flask import Blueprint, request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import json
import psycopg2.extras

# Define the blueprint
assessment_router = Blueprint('assessment', __name__)

def get_retake_details():
    # 1. AUTHENTICATION & STUDENT_ID FETCH
    user_id_str, auth_error = TokenVerifier.get_user_id()
    if not user_id_str: 
        return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
        
    student_id = int(user_id_str)
    payload = request.get_json()
    set_id = payload.get("set_id")
    
    if not set_id:
        return api_response(code=400, status="error", message="set_id is required")

    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False 
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 2. Call the procedure with student_id
        # Updated signature: (set_id, student_id, cursor_name)
        cur.execute("CALL learning.usp_get_retake_questions(%s, %s, 'rs_questions')", (int(set_id), student_id))
        
        # 3. Fetch data
        cur.execute('FETCH ALL IN "rs_questions"')
        rows = cur.fetchall()
        conn.commit()

        if not rows:
            return api_response(code=404, status="error", message="No questions found for this student.", data=[])

        formatted_data = []
        for row in rows:
            parsed_options = row['options']
            if isinstance(parsed_options, str):
                try: parsed_options = json.loads(parsed_options)
                except: parsed_options = []

            formatted_data.append({
                "sl_no": row['sl_no'],
                "question_id": row['question_id'],
                "question_text": row['question_text'],
                "options": parsed_options,
                "difficulty": row['difficulty'],
                "marks": float(round(row['marks'], 2)) if row['marks'] else 0.0,
                "adaptive_level_code": row['adaptive_level_code'],
                "mapped_bucket": row['mapped_bucket'],
                "is_complete": False,
                "is_fallback": False
            })

        cur.close()
        return api_response(code=200, status="success", message="Success", data=formatted_data)

    except Exception as e:
        if conn: conn.rollback()
        return api_response(code=500, status="error", message=f"System Error: {str(e)}")
    finally:
        if conn: conn.close()