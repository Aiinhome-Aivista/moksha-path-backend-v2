from flask import request
from config import get_db_connection, HOST_URL
from utils.api_response import api_response
import psycopg2.extras
import os

BASE_DIR = os.getcwd()
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "blogs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_blogs():

    conn = None
    try:

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_get_blogs(NULL,NULL,NULL)")
        result = cur.fetchone()

        blogs = result["p_object"]

        # attach image url
        if blogs:
            for blog in blogs:
                if blog.get("image"):
                    blog["image"] = f"{HOST_URL}/uploads/blogs/{blog['image']}"

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            data=blogs,
            status="success" if result["p_status_code"] == 200 else "error"
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
            cur.close()
            conn.close()
            
def insert_update_blog():

    conn = None
    try:

        blog_id = request.form.get("id")
        title = request.form.get("blog_title")
        author = request.form.get("blog_author")
        content = request.form.get("blog_content")
        category_id = request.form.get("category_id")
        image_file = request.files.get("image")

        image_name = None

        if image_file and image_file.filename != "":

            image_name = image_file.filename

            image_path = os.path.join(UPLOAD_FOLDER, image_name)

            image_file.save(image_path)
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            "CALL blog.usp_v1_insert_update_blog(%s,%s,%s,%s,%s,%s,NULL,NULL)",
            (blog_id, title, author, content, category_id, image_name)
        )

        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            status="success" if result["p_status_code"] == 200 else "error"
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
            cur.close()
            conn.close()

def delete_blog():

    conn = None
    try:

        body = request.json

        blog_id = body.get("id")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "CALL blog.usp_v1_delete_blog(%s,NULL,NULL)",
            (blog_id,)
        )

        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            status="success" if result["p_status_code"] == 200 else "error"
        )

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))

    finally:
        if conn:
            cur.close()
            conn.close()


def get_public_blogs():

    conn=None

    try:

        conn=get_db_connection()
        cur=conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_get_public_blogs(NULL,NULL,NULL)")
        result=cur.fetchone()

        blogs=result["p_object"]

        if blogs:
            for blog in blogs:

                if blog.get("image"):
                    blog["image"]=f"{HOST_URL}/uploads/blogs/{blog['image']}"

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            data=blogs,
            status="success" if result["p_status_code"]==200 else "error"
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
            cur.close()
            conn.close()