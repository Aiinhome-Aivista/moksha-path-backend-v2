from config import get_db_connection
import psycopg2.extras
from config import get_db_connection
import psycopg2.extras


def get_active_subscription(user_id):

    conn = None

    try:

        conn = get_db_connection()

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Correct way for PROCEDURE
        cur.execute("""
            CALL subscription.usp_v1_get_active_subscription(%s, NULL, NULL, NULL)
        """, (user_id,))

        result = cur.fetchone()

        if result and result.get("o_status") == 200:
            return result.get("o_subscription_id")

        return None

    except Exception as e:

        print("Subscription helper error:", e)
        return None

    finally:

        if conn:
            conn.close()





# from config import get_db_connection
# import psycopg2.extras
# from config import get_db_connection
# import psycopg2.extras


# def get_active_subscription(user_id):

#     conn = None

#     try:

#         conn = get_db_connection()

#         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

#         # Correct way for PROCEDURE
#         cur.execute("""
#             CALL subscription.usp_v1_get_active_subscription(%s, NULL, NULL, NULL)
#         """, (user_id,))

#         result = cur.fetchone()

#         if result and result.get("o_status") == 200:
#             return result.get("o_subscription_id")

#         return None

#     except Exception as e:

#         print("Subscription helper error:", e)
#         return None

#     finally:

#         if conn:
#             conn.close()




# # from config import get_db_connection
# # import psycopg2.extras
# # from config import get_db_connection
# # import psycopg2.extras


# # def get_active_subscription(user_id):

# #     conn = None

# #     try:

# #         conn = get_db_connection()

# #         cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# #         # Correct way for PROCEDURE
# #         cur.execute("""
# #             CALL subscription.subscription.usp_v1_get_active_subscription(%s, NULL, NULL, NULL)
# #         """, (user_id,))

# #         result = cur.fetchone()

# #         if result and result.get("o_status") == 200:
# #             return result.get("o_subscription_id")

# #         return None

# #     except Exception as e:

# #         print("Subscription helper error:", e)
# #         return None

# #     finally:

# #         if conn:
# #             conn.close() 