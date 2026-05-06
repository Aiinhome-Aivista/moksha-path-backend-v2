from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
from utils.remediation_helper import get_remediation_pointers
import psycopg2.extras
import json
import hashlib

def get_data_hash(data):
    """Generates a stable MD5 hash for given data."""
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

def student_remediation_dashboard():
    """
    Returns only the student performance data (Original state, no AI).
    """
    conn = None
    cur = None

    try:
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error")

        user_id = int(user_id_str)

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT final_json
            FROM report.student_remediation_vw
            WHERE user_id = %s
        """, (user_id,))

        row = cur.fetchone()

        if not row:
            return api_response(
                message="No data found",
                code=404,
                status="error"
            )

        data = row.get("final_json")
        if isinstance(data, str):
            data = json.loads(data)

        return api_response(
            message="Student Remediation Dashboard Loaded",
            code=200,
            status="success",
            data=data
        )

    except Exception as e:
        return api_response(
            message="Error fetching remediation dashboard",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def student_remediation_ai_insights():
    """
    Fetches data and returns AI remediation pointers, using a cache to avoid redundant AI calls.
    """
    conn = None
    cur = None
    try:
        user_id_str, _ = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(message="Unauthorized", code=401, status="error")

        user_id = int(user_id_str)
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT final_json
            FROM report.student_remediation_vw
            WHERE user_id = %s
        """, (user_id,))

        row = cur.fetchone()
        if not row:
            return api_response(message="No data found for AI analysis", code=404, status="error")

        student_performance = row.get("final_json")
        if isinstance(student_performance, str):
            student_performance = json.loads(student_performance)

        # 1. Identify which chapters need AI generation
        chapters_to_generate = []
        cached_remediation_map = {} # (subject_id, chapter_id) -> ai_output

        for subject in student_performance.get("subjects", {}).get("list", []):
            subject_id = subject.get("subject_id")
            for chapter in subject.get("chapters", []):
                chapter_id = chapter.get("chapter_id")
                # Hash the performance data (levels) to detect changes
                current_hash = get_data_hash(chapter.get("levels"))

                # Check cache
                cur.execute("""
                    SELECT ai_output, data_hash 
                    FROM report.ai_remediation_cache 
                    WHERE user_id = %s AND subject_id = %s AND chapter_id = %s
                """, (user_id, subject_id, chapter_id))
                
                cache_row = cur.fetchone()

                if cache_row and cache_row["data_hash"] == current_hash:
                    cached_remediation_map[(subject_id, chapter_id)] = cache_row["ai_output"]
                else:
                    chapters_to_generate.append({
                        "subject_id": subject_id,
                        "subject_name": subject.get("subject_name"),
                        "chapter": chapter,
                        "data_hash": current_hash
                    })

        # 2. Call AI for only the "dirty" or new chapters
        if chapters_to_generate:
            # Group by subject for the AI prompt
            grouped_input = {"subjects": {"list": []}}
            subj_map = {}
            for item in chapters_to_generate:
                sid = item["subject_id"]
                if sid not in subj_map:
                    subj_map[sid] = {
                        "subject_id": sid,
                        "subject_name": item["subject_name"],
                        "chapters": []
                    }
                    grouped_input["subjects"]["list"].append(subj_map[sid])
                subj_map[sid]["chapters"].append(item["chapter"])

            # AI Call
            ai_results = get_remediation_pointers(grouped_input)
            
            # 3. Update cache with new results
            if isinstance(ai_results, dict) and "subjects" in ai_results:
                for subj_res in ai_results["subjects"].get("list", []):
                    sid = subj_res.get("subject_id")
                    for chap_res in subj_res.get("chapters", []):
                        chap_id = chap_res.get("chapter_id")
                        
                        # Find the corresponding data_hash
                        match = next((c for c in chapters_to_generate if c["subject_id"] == sid and c["chapter"]["chapter_id"] == chap_id), None)
                        
                        if match:
                            d_hash = match["data_hash"]
                            
                            cur.execute("""
                                INSERT INTO report.ai_remediation_cache (user_id, subject_id, chapter_id, data_hash, ai_output)
                                VALUES (%s, %s, %s, %s, %s)
                                ON CONFLICT (user_id, subject_id, chapter_id)
                                DO UPDATE SET data_hash = EXCLUDED.data_hash, ai_output = EXCLUDED.ai_output, updated_at = NOW()
                            """, (user_id, sid, chap_id, d_hash, json.dumps(chap_res)))
                            
                            cached_remediation_map[(sid, chap_id)] = chap_res
            conn.commit()

        # 4. Assemble final response
        final_remediation = {"subjects": {"list": []}}
        for subject in student_performance.get("subjects", {}).get("list", []):
            sid = subject.get("subject_id")
            new_subj = {
                "subject_id": sid,
                "subject_name": subject.get("subject_name"),
                "chapters": []
            }
            for chapter in subject.get("chapters", []):
                cid = chapter.get("chapter_id")
                pointers = cached_remediation_map.get((sid, cid))
                if pointers:
                    new_subj["chapters"].append(pointers)
            
            if new_subj["chapters"]:
                final_remediation["subjects"]["list"].append(new_subj)

        return api_response(
            message="AI Remediation Insights Generated",
            code=200,
            status="success",
            data={
                "remediation": final_remediation
            }
        )

    except Exception as e:
        if conn: conn.rollback()
        return api_response(message="Error generating AI insights", code=500, status="error", error=str(e))
    finally:
        if cur: cur.close()
        if conn: conn.close()
