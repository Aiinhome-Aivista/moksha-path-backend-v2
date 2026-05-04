from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
import psycopg2.extras
from decimal import Decimal

def clean_data(obj):
    """
    Recursively converts Decimal objects to float/int to avoid scientific notation (0E-20) 
     and string representation in JSON.
    """
    if isinstance(obj, list):
        return [clean_data(i) for i in obj]
    if isinstance(obj, dict):
        return {k: clean_data(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        # If it's a whole number, return as int, otherwise float
        return float(obj) if obj % 1 > 0 else int(obj)
    return obj

def principal_dashboard_kpi():
    """
    Fetches Principal Dashboard KPIs from Part 1 and Part 2 views.
    Merges the responses and returns cleaned data.
    """
    conn = None
    cur = None

    try:
        # 1. Authenticate and get Principal ID from token
        principal_id_str, _ = TokenVerifier.get_user_id()
        if not principal_id_str:
            return api_response(message="Unauthorized", code=401, status="error")

        principal_id = int(principal_id_str)

        # 2. Database Connection
        conn = get_db_connection()
        conn.autocommit = False
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 3. Set the session variable for the views
        cur.execute("SET LOCAL app.principal_id = %s", (principal_id,))

        # 4. Fetch Part 1 KPIs
        cur.execute("SELECT * FROM report.principal_dashboard_kpi_part_1_vw")
        part1 = cur.fetchone()

        # 5. Fetch Part 2 KPIs
        cur.execute("SELECT * FROM report.principal_dashboard_kpi_part_2_vw")
        part2 = cur.fetchone()

        conn.commit()

        # 6. Merge results
        merged_data = {}
        if part1:
            merged_data.update(part1)
        if part2:
            merged_data.update(part2)

        if not merged_data:
             return api_response(
                message="No KPI data found for this principal",
                code=404,
                status="error"
            )

        
        return api_response(
            message="Principal Dashboard KPIs Loaded Successfully",
            code=200,
            status="success",
            data=merged_data
        )

    except Exception as e:
        if conn:
            conn.rollback()
        return api_response(
            message="Error fetching principal dashboard metrics",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
