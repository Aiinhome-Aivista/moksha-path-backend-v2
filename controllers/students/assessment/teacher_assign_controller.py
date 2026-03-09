from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription  # <--- Imported Helper
import psycopg2.extras

# ==========================================
# HELPER FUNCTION (Updated to use DB Helper)
# ==========================================
def get_user_context():
    """
    Extracts User ID from the Token and fetches the active Subscription ID from DB.
    Returns: (user_id, subscription_id, error_message)
    """
    payload = TokenVerifier.get_user_payload()
    if not payload: 
        return None, None, "Unauthorized"
    
    user_id = payload.get('sub')
    
    # <--- ALWAYS fetch latest subscription from DB --->
    subscription_id = get_active_subscription(user_id)
        
    return user_id, subscription_id, None


# ==========================================
# API: Teacher Assign Assessment to Students
# ==========================================
def teacher_assign_assessment():
    """
    POST /api/v1/learning/teacher/assign_assessment
    """
    try:
        # 1. Extract Assigner ID and Subscription from Token/DB
        assigner_id, subscription_id, error = get_user_context()
        if error: return api_response(message=error, code=401, status="error")
        if not subscription_id: return api_response(message="No active subscription found.", code=403, status="error")

        data = request.get_json()
        
        # 2. Extract Data
        student_ids = data.get('student_ids')
        subject_id = data.get('subject_id')
        chapter_ids = data.get('chapter_ids', [])
        total_questions = data.get('total_questions', 10)
        duration_minutes = data.get('duration_minutes', 30)
        
        # Capture Due Date (Pass None if missing)
        due_date = data.get('due_date') 
        
        # Handle Difficulty Map
        raw_diff = str(data.get('difficulty_level', 'Mixed')).strip().lower()
        if raw_diff in ['low', 'easy']: difficulty = 'Easy'
        elif raw_diff == 'medium': difficulty = 'Medium'
        elif raw_diff in ['hard', 'high']: difficulty = 'Hard'
        else: difficulty = 'Mixed'

        # Basic Validation
        if not student_ids or not isinstance(student_ids, list):
            return api_response(message="student_ids list is required", code=400, status="error")
        if not subject_id:
            return api_response(message="subject_id is required", code=400, status="error")
        
        # Clean empty lists for SQL
        if not chapter_ids: chapter_ids = None

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 3. Call the Teacher Specific SP
            # Added %s for subscription_id before the OUT parameters
            cur.execute(
                """
                CALL learning.usp_v1_teacher_assign_assessment(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, '', '{}'::JSONB
                )
                """,
                (
                    assigner_id, 
                    student_ids, 
                    subject_id, 
                    chapter_ids, 
                    total_questions, 
                    duration_minutes, 
                    due_date, 
                    difficulty,
                    subscription_id  # <--- Added subscription ID here
                )
            )
            result = cur.fetchone()
            conn.commit()

            if result['o_status'] == 200:
                return api_response(message=result['o_message'], data=result['o_data'], code=200, status="success")
            else:
                return api_response(message=result['o_message'], code=result['o_status'], status="error")

        except Exception as db_err:
            conn.rollback()
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close(); conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")