import json
import os
import re
import urllib.parse
from flask import request
from config import get_db_connection
from utils.api_response import api_response
from utils.token_helper import TokenVerifier
from psycopg2.extras import Json
from model.llm_client import call_llm

import yt_dlp

def get_youtube_videos(query, max_results=7):

    videos = []

    try:

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            result = ydl.extract_info(
                f"ytsearch{max_results}:{query}",
                download=False
            )

            for video in result.get("entries", []):

                video_id = video.get("id")

                if not video_id:
                    continue

                duration = int(video.get("duration") or 0)

                if duration < 60:
                    continue

                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60

                duration_str = (
                    f"{hours}:{minutes:02d}:{seconds:02d}"
                    if hours > 0 else
                    f"{minutes}:{seconds:02d}"
                )

                videos.append({
                    "title": video.get("title"),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "duration": duration_str
                })

        return videos

    except Exception as e:
        # print(e)
        return []


def get_or_generate_chapter_topic_resources():
    conn = None
    try: 
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return api_response(
                message="Unauthorized",
                code=401,
                status="error",
                error=auth_error
            )

        data = request.get_json()
        # print("INPUT DATA:", data)

        board_id = data.get("board_id")
        institute_id = data.get("institute_id")
        class_id = data.get("class_id")
        subject_id = data.get("subject_id")
        # chapter_id = data.get("chapter_id")
        
        topic_ids = data.get("topic_ids")
        chapter_ids = data.get("chapter_ids")

        if not chapter_ids:
            return api_response(
                message="chapter_ids must be array",
                code=400,
                status="error"
            )

        # ensure always int list
        chapter_ids = [int(c) for c in chapter_ids]


        if not topic_ids or not isinstance(topic_ids, list):
            return api_response(
                message="topic_ids must be array",
                code=400,
                status="error"
            )

        topic_ids = [int(t) for t in topic_ids]

        conn = get_db_connection()
        cur = conn.cursor()   # RealDictCursor comes from config

        # ===================================================
        #  CHECK EXISTING
        # ===================================================
        # print("Calling GET procedure...")

        cur.execute("""
            CALL learning.usp_v2_get_chapter_topic_ai_resources(
                %s,%s,%s,%s,%s,%s,
                %s,%s,%s
            )
        """, (
            board_id,
            institute_id,
            class_id,
            subject_id,
            chapter_ids,
            topic_ids,
            None,
            None,
            None
        ))

        row = cur.fetchone()
        

        existing_data = []

        if row and row.get("p_data"):
            existing_data = row["p_data"]
 

        existing_topic_ids = [
            item["topic_id"]
            for item in existing_data
        ] if existing_data else []

       

        missing_topic_ids = list(set(topic_ids) - set(existing_topic_ids))
         

        # ===================================================
        #  GENERATE MISSING
        # ===================================================
        for topic_id in missing_topic_ids:

           

            cur.execute("""
                CALL learning.usp_v1_get_topic_name(
                    %s,%s,%s,%s
                )
            """, (
                topic_id,
                None,
                None,
                None
            ))

            topic_row = cur.fetchone()

            if not topic_row or topic_row.get("p_status") != "success":
                continue

            topic_name = topic_row["p_topic_name"]

            # 🔹 LLM Prompt
            prompt = f"""Generate detailed structured academic notes for:Topic: {topic_name}
            Class: {class_id}
            Return JSON only:
            {{  "notes": "Full structured academic notes"}}"""

            llm_response = call_llm(prompt)

            match = re.search(r'\{.*\}', llm_response or "", re.DOTALL)
            if not match:
                # print("LLM response invalid")
                continue

            try:
                parsed = json.loads(match.group())
            except Exception as ex:
                print("JSON parse error:", ex)
                continue

            notes = parsed.get("notes")
            if isinstance(notes, dict) or isinstance(notes, list):
               notes = json.dumps(notes)
            if not notes:
                print("No notes generated")
                continue

            

            search_variations = [

            f"{topic_name} Class {class_id} full chapter tutorial",

            f"{topic_name} Class {class_id} solved examples practice questions",

            f"{topic_name} Class {class_id} Hindi medium full explanation",

            f"{topic_name} Class {class_id} Bengali medium full explanation",

            f"{topic_name} Class {class_id} one shot revision"
             ]
      
            youtube_links = []
            seen_urls = set()

            for query in search_variations:

                    videos = get_youtube_videos(query, max_results=7)

                    for video in videos:

                        if video["url"] not in seen_urls:

                            youtube_links.append(video)
                            seen_urls.add(video["url"])

                        if len(youtube_links) >= 10:
                            break

                    if len(youtube_links) >= 10:
                        break

            for chapter_id in chapter_ids:

                cur.execute("""
                    CALL learning.usp_v2_upsert_chapter_topic_ai_resource(
                        %s,%s,%s,%s,%s,%s,
                        %s,%s,%s
                    )
                """, (
                    board_id,
                    institute_id,
                    class_id,
                    subject_id,
                    chapter_id,
                    topic_id,
                    notes,
                    Json(youtube_links),
                    os.getenv("ACTIVE_LLM")
                ))

            conn.commit()
            # --- FIXED INDENTATION ENDS HERE ---

        # ===================================================
        #  FINAL FETCH
        # ===================================================
        

        cur.execute("""
            CALL learning.usp_v2_get_chapter_topic_ai_resources(
                %s,%s,%s,%s,%s,%s,
                %s,%s,%s
            )
        """, (
            board_id,
            institute_id,
            class_id,
            subject_id,
            chapter_ids,
            topic_ids,
            None,
            None,
            None
        ))

        row = cur.fetchone()
     

        final_data = []

        if row and row.get("p_data"):
            final_data = row["p_data"]
 

        return api_response(
            message="Resources ready",
            code=200,
            data=final_data
        )

    except Exception as e:
        
        return api_response(
            message="Internal Server Error",
            code=500,
            status="error",
            error=str(e)
        )

    finally:
        if conn:
            conn.close()