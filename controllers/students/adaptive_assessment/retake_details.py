from flask import Blueprint, request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import json
import psycopg2.extras

# Define the blueprint
assessment_router = Blueprint('assessment', __name__)

def get_retake_details():
    payload = request.get_json()
    set_id = payload.get("set_id")
    
    if not set_id:
        return api_response(code=400, status="error", message="set_id is required")

    conn = None
    try:
        conn = get_db_connection()
        # Disable autocommit to ensure the transaction stays open for the cursor
        conn.autocommit = False 
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 1. Call the procedure. 
        # The procedure OPENS the cursor named 'rs_questions'
        cur.execute("CALL learning.usp_get_retake_questions(%s, 'rs_questions')", (set_id,))
        
        # 2. Immediately FETCH from the same cursor in the same transaction
        cur.execute('FETCH ALL IN "rs_questions"')
        rows = cur.fetchall()

        # 3. Commit the transaction now that we have the data
        conn.commit()

        if not rows:
            return api_response(code=404, status="error", message="No questions found.", data=[])

        formatted_data = []
        for row in rows:
            # Safe JSON parsing for options
            parsed_options = row['options']
            if isinstance(parsed_options, str):
                try:
                    parsed_options = json.loads(parsed_options)
                except:
                    parsed_options = []

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
        if conn:
            conn.rollback() # Rollback on error
        return api_response(code=500, status="error", message=f"Database Error: {str(e)}")
    finally:
        if conn:
            conn.close()