# from flask import request
# from config import get_db_connection
# from utils.subscription_helper import get_active_subscription
# from utils.token_helper import TokenVerifier
# from utils.api_response import api_response
# import psycopg2.extras

 

# # def assign_auto_assessment():
# #     """
# #     POST /api/v1/learning/assign_auto_assessment
# #     """
# #     try:
# #         # 1. Get Full User Payload
# #         payload = TokenVerifier.get_user_payload()
# #         if not payload:
# #             return api_response(message="Unauthorized", code=401, status="error")
            
# #         assigner_id = int(payload.get('sub'))

# #         # 2. ALWAYS fetch latest subscription from DB using helper
# #         subscription_id = get_active_subscription(assigner_id)

# #         if not subscription_id:
# #              return api_response(message="Active Subscription ID not found for this user.", code=403, status="error")

# #         # 3. Get Request Data
# #         data = request.get_json()
# #         target_student_id = data.get('student_id')
# #         subject_id = data.get('subject_id')
# #         chapter_ids = data.get('chapter_ids') # Expected list: [1, 2] or null
# #         topic_ids = data.get('topic_ids')     # Expected list: [3, 4] or null
# #         test_name = data.get('test_name')     # Expected string or null
        
# #         # Defaults
# #         total_questions = data.get('total_questions', 10)
# #         duration_minutes = data.get('duration_minutes', 30)
# #         passed_role = data.get('role')
        
# #         # Capture Due Date
# #         due_date = data.get('due_date') 

# #         # Difficulty Mapping
# #         raw_diff = str(data.get('difficulty_level', 'Mixed')).strip().lower()
# #         if raw_diff in ['low', 'easy']: difficulty = 'Easy'
# #         elif raw_diff == 'medium': difficulty = 'Medium'
# #         elif raw_diff in ['hard', 'high']: difficulty = 'Hard'
# #         else: difficulty = 'Mixed'

# #         if not subject_id:
# #             return api_response(message="Subject ID is required.", code=400, status="error")

# #         # Convert empty lists to None so SQL handles it correctly
# #         if chapter_ids == [] or not chapter_ids:
# #             chapter_ids = None
# #         if topic_ids == [] or not topic_ids:
# #             topic_ids = None

# #         # Logic: Self vs Teacher assignment
# #         if not target_student_id:
# #             target_student_id = assigner_id
        
# #         if str(assigner_id) == str(target_student_id):
# #             role = 'Student'
# #         else:
# #             role = passed_role if passed_role else 'Teacher'

# #         conn = get_db_connection()
# #         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# #         try:
# #             # 4. Call Procedure with new parameters
# #             cur.execute(
# #                 """
# #                 CALL learning.usp_v1_auto_generate_and_assign(
# #                     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, '', '{}'::JSONB)
# #                 """,
# #                 (
# #                     assigner_id, 
# #                     target_student_id, 
# #                     role, 
# #                     subject_id, 
# #                     chapter_ids, 
# #                     topic_ids,         # <--- New Parameter
# #                     test_name,         # <--- New Parameter
# #                     total_questions, 
# #                     duration_minutes, 
# #                     due_date, 
# #                     difficulty,
# #                     subscription_id  
# #                 )
# #             )
# #             result = cur.fetchone()
# #             conn.commit()

# #             if result['o_status'] == 200:
# #                 return api_response(message=result['o_message'], data=result['o_data'], code=200, status="success")
# #             else:
# #                 return api_response(message=result['o_message'], code=result['o_status'], status="error")

# #         except Exception as db_err:
# #             conn.rollback()
# #             return api_response(message="Database Error", error=str(db_err), code=500, status="error")
# #         finally:
# #             cur.close()
# #             conn.close()

# #     except Exception as e:
# #         return api_response(message="Server Error", error=str(e), code=500, status="error")



# def assign_auto_assessment():
#     """
#     POST /api/v1/learning/assign_auto_assessment
#     """
#     try:
#         # 1. Get Full User Payload
#         payload = TokenVerifier.get_user_payload()
#         if not payload:
#             return api_response(message="Unauthorized", code=401, status="error")
            
#         assigner_id = int(payload.get('sub'))

#         # 2. ALWAYS fetch latest subscription from DB using helper
#         subscription_id = get_active_subscription(assigner_id)

#         if not subscription_id:
#              return api_response(message="Active Subscription ID not found for this user.", code=403, status="error")

#         # 3. Get Request Data
#         data = request.get_json()
#         target_student_id = data.get('student_id')
#         subject_id = data.get('subject_id')
#         chapter_ids = data.get('chapter_ids') 
#         topic_ids = data.get('topic_ids')     
#         test_name = data.get('test_name')     
        
#         # Defaults
#         total_questions = data.get('total_questions', 10)
#         duration_minutes = data.get('duration_minutes', 30)
#         passed_role = data.get('role')
#         due_date = data.get('due_date') 

#         # Difficulty Mapping
#         raw_diff = str(data.get('difficulty_level', 'Mixed')).strip().lower()
#         if raw_diff in ['low', 'easy']: difficulty = 'Easy'
#         elif raw_diff == 'medium': difficulty = 'Medium'
#         elif raw_diff in ['hard', 'high']: difficulty = 'Hard'
#         else: difficulty = 'Mixed'

#         if not subject_id:
#             return api_response(message="Subject ID is required.", code=400, status="error")

#         # Convert empty lists to None so SQL handles it correctly
#         if chapter_ids == [] or not chapter_ids:
#             chapter_ids = None
#         if topic_ids == [] or not topic_ids:
#             topic_ids = None

#         # Logic: Self vs Teacher assignment
#         if not target_student_id:
#             target_student_id = assigner_id
        
#         if str(assigner_id) == str(target_student_id):
#             role = 'Student'
#         else:
#             role = passed_role if passed_role else 'Teacher'

#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         try:
#             # 4. Call Procedure 
#             cur.execute(
#                 """
#                 CALL learning.usp_v2_auto_generate_and_assign(
#                     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, '', '{}'::JSONB)
#                 """,
#                 (
#                     assigner_id, 
#                     target_student_id, 
#                     role, 
#                     subject_id, 
#                     chapter_ids, 
#                     topic_ids,         
#                     test_name,         
#                     total_questions, 
#                     duration_minutes, 
#                     due_date, 
#                     difficulty,
#                     subscription_id  
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
#             cur.close()
#             conn.close()

#     except Exception as e:
#         return api_response(message="Server Error", error=str(e), code=500, status="error")



from flask import request
from config import get_db_connection
from utils.subscription_helper import get_active_subscription
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras

def assign_auto_assessment():
    """
    POST /api/v1/learning/assign_auto_assessment
    """
    try:
        # 1. Get Full User Payload
        payload = TokenVerifier.get_user_payload()
        if not payload:
            return api_response(message="Unauthorized", code=401, status="error")
            
        assigner_id = int(payload.get('sub'))

        # 2. ALWAYS fetch latest subscription from DB using helper
        subscription_id = get_active_subscription(assigner_id)

        if not subscription_id:
             return api_response(message="Active Subscription ID not found for this user.", code=403, status="error")

        # 3. Get Request Data
        data = request.get_json()
        target_student_id = data.get('student_id')
        subject_id = data.get('subject_id')
        chapter_ids = data.get('chapter_ids') 
        topic_ids = data.get('topic_ids')     
        test_name = data.get('test_name')     
        
        # Defaults
        total_questions = data.get('total_questions', 10)
        duration_minutes = data.get('duration_minutes', 30)
        passed_role = data.get('role')
        due_date = data.get('due_date') 

        # Difficulty Mapping
        raw_diff = str(data.get('difficulty_level', 'Mixed')).strip().lower()
        if raw_diff in ['low', 'easy']: difficulty = 'Easy'
        elif raw_diff == 'medium': difficulty = 'Medium'
        elif raw_diff in ['hard', 'high']: difficulty = 'Hard'
        else: difficulty = 'Mixed'

        if not subject_id:
            return api_response(message="Subject ID is required.", code=400, status="error")

        # Convert empty lists to None so SQL handles it correctly
        if chapter_ids == [] or not chapter_ids:
            chapter_ids = None
        if topic_ids == [] or not topic_ids:
            topic_ids = None

        # Logic: Self vs Teacher assignment
        if not target_student_id:
            target_student_id = assigner_id
        
        if str(assigner_id) == str(target_student_id):
            role = 'Student'
        else:
            role = passed_role if passed_role else 'Teacher'

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # 4. Call Procedure (Calling the new V3 version!)
            cur.execute(
                """
                CALL learning.usp_v3_auto_generate_and_assign(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, '', '{}'::JSONB)
                """,
                (
                    assigner_id, 
                    target_student_id, 
                    role, 
                    subject_id, 
                    chapter_ids, 
                    topic_ids,         
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

            # The SP will return 403 if the user exceeds their plan's max_assessments
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