from flask import request
from config import get_db_connection, HOST_URL
from utils.api_response import api_response



def get_public_blogs():

    conn=None

    try:

        conn=get_db_connection()
        cur=conn.cursor()

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