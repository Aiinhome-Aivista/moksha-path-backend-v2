from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription  # <--- Imported Helper
import psycopg2.extras

# ==========================================
# HELPER: Get User Context from Token & DB
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
# HELPER: Fetch Board ID for Teacher
# ==========================================
def get_teacher_board_id(teacher_id, conn):
    """
    Fetches the Board ID associated with the Teacher from the DB.
    Assumes Teacher is mapped in master.board_class_user_mapping
    """
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Fetch the first active board mapping for this teacher
        cur.execute("""
            SELECT board_id 
            FROM master.board_class_user_mapping 
            WHERE user_id = %s AND is_active = TRUE 
            LIMIT 1
        """, (teacher_id,))
        res = cur.fetchone()
        cur.close()
        
        if res and res['board_id']:
            return res['board_id']
        return None
    except Exception:
        return None

# ==========================================
# API: Assign Assessment to Class
# ==========================================
# def teacher_assign_class_assessment():
#     """
#     POST /api/v1/teacher/assign_class_assessment
#     """
#     try:
#         # 1. Get Teacher Context (ID and Subscription)
#         assigner_id, subscription_id, error = get_user_context()
#         if error: return api_response(message=error, code=401)
#         if not subscription_id: return api_response(message="No active subscription found.", code=403)

#         conn = get_db_connection()
        
#         # 2. Fetch Board ID using User ID (Database Lookup)
#         board_id = get_teacher_board_id(assigner_id, conn)
        
#         if not board_id:
#             conn.close()
#             return api_response(message="Teacher is not linked to any Board. Cannot assign assessment.", code=403)

#         # 3. Get Payload
#         data = request.get_json()
#         class_ids = data.get('class_ids')
#         subject_id = data.get('subject_id')
#         chapter_ids = data.get('chapter_ids', [])
#         total_questions = data.get('total_questions', 10)
#         duration_minutes = data.get('duration_minutes', 45)
#         difficulty = data.get('difficulty_level', 'Mixed')
#         due_date = data.get('due_date')

#         if not class_ids or not subject_id:
#             conn.close()
#             return api_response(message="Class IDs and Subject ID are required.", code=400)

#         # Sanitize empty lists for PostgreSQL
#         if chapter_ids == [] or not chapter_ids:
#             chapter_ids = None

#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         try:
#             # 4. Call Stored Procedure
#             # cur.execute(
#             #     """
#             #     CALL learning.usp_v1_teacher_assign_assessment_by_class(
#             #         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, '', '{}'::jsonb
#             #     )
#             #     """,
#             #     (
#             #         assigner_id,
#             #         board_id,       # <--- Passed from DB Lookup
#             #         class_ids,
#             #         subject_id,
#             #         chapter_ids,
#             #         total_questions,
#             #         duration_minutes,
#             #         due_date,
#             #         difficulty,
#             #         subscription_id # <--- Passed from Helper
#             #     )
#             # )
            
            
#             cur.execute(
#                 """
#                 CALL learning.usp_v2_teacher_assign_assessment_by_class(
#                     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, '', '{}'::jsonb
#                 )
#                 """,
#                 (
#                     assigner_id,
#                     board_id,       # <--- Passed from DB Lookup
#                     class_ids,
#                     subject_id,
#                     chapter_ids,
#                     total_questions,
#                     duration_minutes,
#                     due_date,
#                     difficulty,
#                     subscription_id # <--- Passed from Helper
#                 )
#             )
             
#             result = cur.fetchone()
#             conn.commit()

#             if result['o_status'] == 200:
#                 return api_response(message=result['o_message'], data=result['o_data'], code=200, status="success")
#             else:
#                 return api_response(message=result['o_message'], code=result['o_status'], status="error")

#         except Exception as db_err:
#             conn.rollback()
#             return api_response(message="Database Error", error=str(db_err), code=500, status="error")
#         finally:
#             cur.close(); conn.close()

#     except Exception as e:
#         return api_response(message="Server Error", error=str(e), code=500, status="error")




 

def teacher_assign_class_assessment():
    """
    POST /api/v1/teacher/assign_class_assessment
    """
    try:
        # 1. Get Teacher Context (ID and Subscription)
        assigner_id, subscription_id, error = get_user_context()
        if error: return api_response(message=error, code=401)
        if not subscription_id: return api_response(message="No active subscription found.", code=403)

        conn = get_db_connection()
        
        # 2. Fetch Board ID using User ID (Database Lookup)
        board_id = get_teacher_board_id(assigner_id, conn) 
        
        if not board_id:
            conn.close()
            return api_response(message="Teacher is not linked to any Board. Cannot assign assessment.", code=403)

        # 3. Get Payload
        data = request.get_json()
        class_ids = data.get('class_ids')
        student_ids = data.get('student_ids', []) 
        subject_id = data.get('subject_id')
        chapter_ids = data.get('chapter_ids', [])
        topic_ids = data.get('topic_ids', [])       # <--- Fetch specific topics
        test_name = data.get('test_name') 
        total_questions = data.get('total_questions', 10)
        duration_minutes = data.get('duration_minutes', 45)
        difficulty = data.get('difficulty_level', 'Mixed')
        due_date = data.get('due_date')

        if not class_ids or not subject_id:
            conn.close()
            return api_response(message="Class IDs and Subject ID are required.", code=400)

        # Sanitize empty lists to None for PostgreSQL
        if not chapter_ids: chapter_ids = None
        if not topic_ids: topic_ids = None         # <--- Converts [] or None to None
        if not student_ids: student_ids = None

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try: 
            cur.execute(
                """
                CALL learning.usp_v3_teacher_assign_assessment_by_class(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, '', '{}'::jsonb
                )
                """,
                (
                    assigner_id,
                    board_id,        
                    class_ids,
                    student_ids,     
                    subject_id,
                    chapter_ids,
                    topic_ids,       # <--- Pass the new topic_ids parameter
                    test_name,       
                    total_questions,
                    duration_minutes,
                    due_date,
                    difficulty,
                    subscription_id  
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
            cur.close()
            conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")