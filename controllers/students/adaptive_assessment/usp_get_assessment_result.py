from flask import Blueprint, request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
import json
import psycopg2.extras


assessment_router = Blueprint('assessment', __name__)

 
def get_assessment_result():
    # 1. AUTH: Get ID from token (No need to pass in body)
    user_id_str, auth_error = TokenVerifier.get_user_id()
    if not user_id_str: 
        return api_response(message="Unauthorized", code=401, status="error", error=auth_error)
    
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False 
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 2. CALL PROCEDURE
        cur.execute("CALL learning.usp_get_all_completed_assessments(%s, 'rs_results')", (int(user_id_str),))
        
        # 3. FETCH FROM CURSOR
        cur.execute('FETCH ALL IN "rs_results"')
        rows = cur.fetchall()
        conn.commit()

        return api_response(
            code=200,
            status="success",
            message="Records fetched successfully.",
            data=rows if rows else []
        )

    except Exception as e:
        if conn: conn.rollback()
        return api_response(message="System Error", code=500, status="error", error=str(e))
    finally:
        if conn: conn.close()