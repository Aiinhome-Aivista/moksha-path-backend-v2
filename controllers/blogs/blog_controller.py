from flask import request
from config import get_db_connection, HOST_URL
from utils.api_response import api_response
import os
import psycopg2.extras

# Define constants for file handling
BASE_DIR = "/home/site/wwwroot"
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "blogs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# blogs
# get_blogs
def get_blogs():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("CALL blog.usp_v1_get_blogs(NULL,NULL,NULL)")
        result = cur.fetchone()

        blogs = result["p_object"]

        # Attach image URL
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

# insert_update_blog
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
        cur = conn.cursor()

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

# delete_blog
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

# get_public_blogs
def get_public_blogs():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("CALL blog.usp_v1_get_public_blogs(NULL,NULL,NULL)")
        result = cur.fetchone()

        blogs = result["p_object"]

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


# category
# get_categories
def get_categories():
    conn = None
    try:

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_get_categories(NULL,NULL,NULL)")
        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            data=result["p_object"],
            status="success" if result["p_status_code"] == 200 else "error"
        )

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))

    finally:
        if conn:
            cur.close()
            conn.close()


# insert_update_category
def insert_update_category():

    conn = None
    try:

        body = request.json

        category_id = body.get("id")
        category_name = body.get("category_name")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "CALL blog.usp_v1_insert_update_category(%s,%s,NULL,NULL)",
            (category_id, category_name)
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


# delete_category
def delete_category():

    conn = None
    try:

        body = request.json

        category_id = body.get("id")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "CALL blog.usp_v1_delete_category(%s,NULL,NULL)",
            (category_id,)
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
            
            
# get_category_dropdown
def get_category_dropdown():

    conn = None
    try:

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_get_category_dropdown(NULL,NULL,NULL)")
        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            data=result["p_object"],
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


# seo
# get_seo_settings
def get_seo_settings():

    conn = None
    try:

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_get_seo_settings(NULL,NULL,NULL)")
        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            data=result["p_object"],
            status="success" if result["p_status_code"] == 200 else "error"
        )

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))

    finally:
        if conn:
            cur.close()
            conn.close()


# insert_update_seo
def insert_update_seo():

    conn = None
    try:

        body = request.json

        seo_id = body.get("id")
        route = body.get("page_route")
        title = body.get("seo_title")
        description = body.get("seo_description")
        keywords = body.get("seo_keywords")
        canonical = body.get("canonical_url")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "CALL blog.usp_v1_insert_update_seo_settings(%s,%s,%s,%s,%s,%s,NULL,NULL)",
            (seo_id, route, title, description, keywords, canonical)
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
            
            
# delete_seo
def delete_seo():

    conn = None
    try:

        body = request.json

        seo_id = body.get("id")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            "CALL blog.usp_v1_delete_seo_settings(%s,NULL,NULL)",
            (seo_id,)
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


# authors
# get_authors
def get_authors():
    conn = None
    try:

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_get_authors(NULL,NULL,NULL)")
        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            data=result["p_object"],
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



# admin
# admin_login
def admin_login():
    conn = None
    try:

        body = request.json

        username = body.get("username")
        password = body.get("password")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_admin_login(%s,%s,NULL,NULL,NULL)", (username, password))

        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            data=result["p_object"],
            status="success" if result["p_status_code"] == 200 else "error"
        )

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))

    finally:
        if conn:
            cur.close()
            conn.close()


# admin_get_dashboard
def admin_get_dashboard():

    conn = None
    try:

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("CALL blog.usp_v1_dashboard(NULL,NULL,NULL)")
        result = cur.fetchone()

        return api_response(
            message=result["p_msg"],
            code=result["p_status_code"],
            data=result["p_object"],
            status="success" if result["p_status_code"] == 200 else "error"
        )

    except Exception as e:
        return api_response(message="Internal Server Error", code=500, status="error", error=str(e))

    finally:
        if conn:
            cur.close()
            conn.close()