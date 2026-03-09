from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras

def _get_teacher_context():
    """Helper to extract teacher_id and subscription_id from token payload"""
    payload = TokenVerifier.get_user_payload()
    if not payload:
        return None, None, "Unauthorized: Invalid token"
    
    teacher_id = payload.get('sub')
    subscription_id = payload.get('subscription_id') or payload.get('sub_id') or payload.get('sid')
    
    if not teacher_id:
        return None, None, "Unauthorized: Missing user identity."
    if not subscription_id:
        return None, None, "Unauthorized: No active subscription found in token. Please switch profile."
    
    return int(teacher_id), subscription_id, None

# 1. Bucket-wise Performance Analysis
def get_bucket_performance():
    conn = None
    try:
        teacher_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        class_id = request.args.get('class_id', type=int)
        section_id = request.args.get('section_id', type=int)
        subject_id = request.args.get('subject_id', type=int)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # CHANGED TO sp_v3
        cur.execute(
            "CALL learning.sp_v4_teacher_bucket_performance(%s, %s, %s, %s, %s, NULL, NULL, NULL)", 
            (teacher_id, subscription_id, class_id, section_id, subject_id)
        )
        result = cur.fetchone()
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 2. Teacher Subject Mapping
def get_teacher_subjects():
    conn = None
    try:
        teacher_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("CALL learning.sp_v2_teacher_subjects(%s, %s, NULL, NULL, NULL)", (teacher_id, subscription_id))
        result = cur.fetchone()
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 3. Subject-wise Performance Overview
def get_subject_performance():
    conn = None
    try:
        teacher_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        subject_id = request.args.get('subject_id', type=int)
        if not subject_id: return api_response(message="subject_id is required", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # CHANGED TO sp_v3
        cur.execute("CALL learning.sp_v3_teacher_subject_performance(%s, %s, %s, NULL, NULL, NULL)", (teacher_id, subscription_id, subject_id))
        result = cur.fetchone()
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 4. Chapter-wise Performance Analysis
def get_chapter_performance():
    conn = None
    try:
        teacher_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        subject_id = request.args.get('subject_id', type=int)
        if not subject_id: return api_response(message="subject_id is required", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # CHANGED TO sp_v3
        cur.execute("CALL learning.sp_v4_teacher_chapter_performance(%s, %s, %s, NULL, NULL, NULL)", (teacher_id, subscription_id, subject_id))
        result = cur.fetchone()
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# # 5. Class-Level Exam Performance
# def get_class_exam_performance():
#     conn = None
#     try:
#         teacher_id, subscription_id, err = _get_teacher_context()
#         if err: return api_response(message=err, code=403, status="error")

#         # Get them if they exist, but don't force them
#         class_id = request.args.get('class_id', type=int)
#         set_id = request.args.get('set_id', type=int)

#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#         # CHANGED TO sp_v3
#         cur.execute("CALL learning.sp_v4_teacher_class_exam_performance(%s, %s, %s, %s, NULL, NULL, NULL)", 
#                     (teacher_id, subscription_id, class_id, set_id))
#         result = cur.fetchone()
#         return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()
# 5. Class-Level Exam Performance
def get_class_exam_performance():
    conn = None
    try:
        teacher_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        # Completely removed the request.args.get for class_id and set_id

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Pass NULLs dynamically to the database
        cur.execute(
            "CALL learning.sp_v5_teacher_class_exam_performance(%s, %s, NULL, NULL, NULL, NULL, NULL)", 
            (teacher_id, subscription_id)
        )
        result = cur.fetchone()
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 6. Curriculum Coverage
def get_curriculum_coverage():
    """ GET /api/v1/parent_teacher/dashboard/curriculum-coverage """
    conn = None
    try:
        teacher_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # CHANGED TO sp_v3
        cur.execute(
            "CALL learning.sp_v4_teacher_curriculum_coverage(%s, %s, NULL, NULL, NULL)", 
            (teacher_id, subscription_id)
        )
        result = cur.fetchone()
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 7. Upcoming Chapters (Based on Subject)
def get_upcoming_chapters():
    """ GET /api/v1/parent_teacher/dashboard/upcoming-chapters?subject_id=XYZ """
    conn = None
    try:
        teacher_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        subject_id = request.args.get('subject_id', type=int)
        if not subject_id: return api_response(message="subject_id is required", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("CALL learning.sp_v2_teacher_upcoming_chapters(%s, %s, %s, NULL, NULL, NULL)", (teacher_id, subscription_id, subject_id))
        result = cur.fetchone()
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 8. Pending Topics (Today)
# 8. Pending Topics (Filtered by Subject)
def get_pending_topics():
    """ GET /api/v1/parent_teacher/dashboard/pending-topics """
    conn = None
    try:
        teacher_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        # Get the subject_id if it's passed from the frontend dropdown
        subject_id = request.args.get('subject_id', type=int)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Call the new V4 procedure
        cur.execute("CALL learning.sp_v5_teacher_pending_topics(%s, %s, %s, NULL, NULL, NULL)", (teacher_id, subscription_id, subject_id))
        result = cur.fetchone()
        
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()

# 9. Teacher Profile Details (Name, School, Class)
def get_teacher_profile_details():
    """ GET /api/v1/parent_teacher/dashboard/teacher-profile """
    conn = None
    try:
        teacher_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("CALL learning.sp_v1_teacher_profile_details(%s, %s, NULL, NULL, NULL)", (teacher_id, subscription_id))
        result = cur.fetchone()
        
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()


# 10. Top 20 & Lowest 20 Students (Subject Wise)
def get_teacher_top_bottom_students():
    """ GET /api/v1/parent_teacher/dashboard/top-bottom-students?subject_id=XYZ """
    conn = None
    try:
        teacher_id, subscription_id, err = _get_teacher_context()
        if err: return api_response(message=err, code=403, status="error")

        subject_id = request.args.get('subject_id', type=int)
        if not subject_id: return api_response(message="subject_id is required", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("CALL learning.sp_v1_teacher_top_bottom_students(%s, %s, %s, NULL, NULL, NULL)", (teacher_id, subscription_id, subject_id))
        result = cur.fetchone()
        
        return api_response(message=result['o_message'], code=result['o_status'], data=result['o_data'])
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")
    finally:
        if conn: conn.close()