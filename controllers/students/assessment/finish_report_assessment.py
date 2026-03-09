from flask import request
from config import get_db_connection
from utils.token_helper import TokenVerifier
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription  
import psycopg2.extras

# ==========================================
# HELPER FUNCTION
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
# BATCH PROCESS & GENERATE REPORT (AUTOMATED)
# ==========================================
def process_evaluation_data():
    """
    POST /api/v1/learning/evaluation/process_all
    Triggers:
      1. Batch Processing (Datamart Schema -> evaluation_stage table)
      2. Report Population (Report Schema -> evaluation_report table)
    """
    try:
        # 1. Get User Context
        user_id, subscription_id, error = get_user_context()
        if error: 
            return api_response(message=error, code=401)
        if not subscription_id: 
            return api_response(message="No active subscription found in token.", code=403)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # ---------------------------------------------------------
            # STEP 1: Process Raw Data into Datamart (Calls 'datamart' schema)
            # ---------------------------------------------------------
            cur.execute(
                "CALL datamart.usp_v1_batch_process_user_evaluations(%s, %s, 0, '', 0)", 
                (user_id, subscription_id)
            )
            batch_res = cur.fetchone()
            batch_count = batch_res.get('o_count', 0)

            report_count = 0
            
            # ---------------------------------------------------------
            # STEP 2: Populate Final Report (Calls 'report' schema)
            # ---------------------------------------------------------
            if batch_count > 0:
                cur.execute("CALL report.usp_v1_populate_evaluation_report(0, '', 0)")
                report_res = cur.fetchone() 
                report_count = report_res.get('o_count', 0)
            
            conn.commit()
            
            # Construct a dynamic success message based on what happened
            if batch_count == 0:
                final_message = "All caught up! No new assessments to process."
            else:
                final_message = f"Batch Processed: {batch_count} new evaluated questions. Report Updated: {report_count} topics."
            
            return api_response(
                message=final_message, 
                code=200,
                status="success"
            )

        except Exception as db_err:
            conn.rollback()
            return api_response(message="Database Error during processing", error=str(db_err), code=500)
            
        finally:
            cur.close(); conn.close()
            
    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500)


# ==========================================
# GET DASHBOARD REPORT
# ==========================================
def get_evaluation_dashboard():
    """
    GET /api/v1/learning/report/student
    Optional Query Param: ?subject_id=1
    """
    try:
        # 1. Get User Context
        user_id, subscription_id, error = get_user_context()
        if error: return api_response(message=error, code=401)
        if not subscription_id: return api_response(message="No active subscription found.", code=403)

        # 2. Optional Subject Filter
        subject_id = request.args.get('subject_id') 

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Call the stored procedure (Calls 'report' schema)
            cur.execute(
                "CALL report.usp_v1_get_student_report(%s, %s, 0, '', '{}')", 
                (subscription_id, subject_id if subject_id else None)
            )
            res = cur.fetchone()
            
            return api_response(
                message=res['o_message'], 
                data=res['o_data'], 
                code=res['o_status']
            )
            
        finally:
            cur.close(); conn.close()
            
    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500)