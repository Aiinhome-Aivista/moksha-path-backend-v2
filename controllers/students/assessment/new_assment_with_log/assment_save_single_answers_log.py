from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import psycopg2.extras

 
def assment_save_single_answers_log():
    try:
        # 1. Get User ID from Token
        student_id, error = TokenVerifier.get_user_id()
        if error: 
            return api_response(message=error, code=401, status="error")

        data = request.get_json()
        if not data:
            return api_response(message="Request body is empty", code=400, status="error")
        
        # 2. Extract Data
        attempt_id = data.get('attempt_id')
        question_id = data.get('question_id')
        sl_no = data.get('sl_no') 
        answer = data.get('answer')
        time_taken = data.get('time_taken')

        # Basic Validation
        if not all([attempt_id, question_id, answer]):
            return api_response(message="attempt_id, question_id, and answer are required.", code=400, status="error")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # 3. Call Procedure (Explicitly casting to BIGINT to match the new SP signature)
            cur.execute(
                """
                CALL learning.usp_log_save_single_answer_v1(
                    %s::BIGINT, 
                    %s::BIGINT, 
                    %s::BIGINT, 
                    %s::BIGINT, 
                    %s::TEXT, 
                    %s::BIGINT, 
                    0, 
                    ''
                )
                """, 
                (
                    int(attempt_id), 
                    int(student_id), 
                    int(question_id), 
                    int(sl_no) if sl_no is not None else 0, 
                    str(answer), 
                    int(time_taken or 0)
                )
            )
            res = cur.fetchone()
            conn.commit()
            
            # 4. Handle Response
            if res['o_status'] == 200:
                return api_response(message=res['o_message'], code=200, status="success")
            else:
                return api_response(message=res['o_message'], code=res['o_status'], status="error")
                
        except Exception as db_err:
            conn.rollback()
            return api_response(message="Database Error", error=str(db_err), code=500, status="error")
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")