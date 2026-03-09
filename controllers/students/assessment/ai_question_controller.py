# from flask import request
# from config import get_db_connection
# from utils.api_response import api_response
# from utils.ai_generator import generate_questions_with_ai
# import psycopg2.extras
# import json

# def generate_and_store_questions():
#     """
#     POST /api/v1/learning/store_questions
#     """
#     conn = None
#     try:
#         data = request.get_json()
#         institute_id = data.get('institute_id')
#         board_id = data.get('board_id')
#         class_id = data.get('class_id')
#         subject_id = data.get('subject_id')

#         if not all([board_id, class_id, subject_id]):
#             return api_response(message="Missing required IDs", code=400, status="error")

#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         # ---------------------------------------------------------
#         # STEP 1: Get Work List (Metadata + Topics needing questions)
#         # ---------------------------------------------------------
#         try:
#             # Calls the new Stored Procedure
#             cur.execute(
#                 "CALL learning.usp_v1_get_topics_for_ai_generation(%s, %s, %s, 0, '', '{}', '{}')",
#                 (board_id, class_id, subject_id)
#             )
#             work_data = cur.fetchone()
#             conn.commit()

#             if work_data['o_status'] != 200:
#                 return api_response(message=work_data['o_message'], code=work_data['o_status'], status="error")
            
#             # Extract Data
#             metadata = work_data['o_metadata']
#             topics_to_process = work_data['o_topics']

#             if not topics_to_process:
#                 return api_response(message="All topics already have questions. Nothing to generate.", code=200, status="success")

#         except Exception as db_err:
#             return api_response(message="DB Fetch Error", error=str(db_err), code=500, status="error")

#         # ---------------------------------------------------------
#         # STEP 2: Loop & Generate (Only for topics returned by DB)
#         # ---------------------------------------------------------
#         total_generated = 0
        
#         for topic in topics_to_process:
#             t_id = topic['topic_id']
#             t_name = topic['topic_name']
#             c_id = topic['chapter_id']

#             print(f"Generating for Topic: {t_name}...")
            
#             # Call AI (Mistral/Gemini)
#             ai_questions = generate_questions_with_ai(
#                 metadata['board_name'], 
#                 metadata['class_name'], 
#                 metadata['subject_name'], 
#                 t_name, 
#                 count=5
#             )

#             if ai_questions:
#                 # Add IDs for the DB insert
#                 for q in ai_questions:
#                     q['institute_id'] = institute_id
#                     q['board_id'] = board_id
#                     q['class_id'] = class_id
#                     q['subject_id'] = subject_id
#                     q['chapter_id'] = c_id
#                     q['topic_id'] = t_id
                
#                 # Store Batch using Procedure
#                 try:
#                     cur.execute(
#                         "CALL learning.usp_v1_store_ai_questions(%s, 0, '')",
#                         (json.dumps(ai_questions),)
#                     )
#                     conn.commit()
#                     total_generated += len(ai_questions)
#                 except Exception as save_err:
#                     conn.rollback()
#                     print(f"Failed to save questions for {t_name}: {str(save_err)}")

#         return api_response(
#             message=f"Process completed. Generated {total_generated} new questions.", 
#             code=200, 
#             status="success"
#         )

#     except Exception as e:
#         return api_response(message="Server Error", error=str(e), code=500, status="error")
#     finally:
#         if conn: conn.close()