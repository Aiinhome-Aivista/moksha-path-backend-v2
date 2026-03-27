 
# from flask import request
# import jwt
# import datetime
# from config import JWT_SECRET

# class TokenVerifier:
#     @staticmethod
#     def get_user_id():
#         """
#         Extracts user_id from the Authorization header in the global Flask request object.
#         Returns: (user_id, error_message)
#         """
#         token = request.headers.get('Authorization')
#         if not token:
#             return None, "Missing Authorization Header"

#         try:
#             if "Bearer" in token:
#                 token = token.split(" ")[1]
            
#             # Decode token
#             decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
#             return decoded.get('sub'), None

#         except jwt.ExpiredSignatureError:
#             return None, "Token has expired"
#         except jwt.InvalidTokenError:
#             return None, "Invalid Token"
#         except Exception as e:
#             return None, f"Auth Error: {str(e)}"

#     # ---------------------------------------------------------
#     # NEW METHOD ADDED HERE (Does not break existing code)
#     # ---------------------------------------------------------
#     @staticmethod
#     def get_user_payload():
#         """
#         Extracts the FULL payload (claims) from the token.
#         Returns: dict (payload) or None
#         """
#         token = request.headers.get('Authorization')
#         if not token:
#             return None

#         try:
#             if "Bearer" in token:
#                 token = token.split(" ")[1]
            
#             # Decode token
#             decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
#             return decoded 

#         except Exception as e:
#             print(f"Token Error: {str(e)}")
#             return None


# class TokenGenerator:
#     @staticmethod
#     def generate_profile_token(user_id, email, mobile, name, username, role_id, roles, sid, sub_id):
#         """
#         Generates a new JWT specific to the selected Profile, perfectly matching the login token structure.
#         """
#         payload = {
#             'sub': str(user_id),
#             'email': email,
#             'mobile': mobile,
#             'name': name,
#             'username': username,
#             'role_id': role_id,
#             'roles': roles if roles else [],
#             'sid': str(sid) if sid else None, # Preserves original login session ID
#             'sub_id': sub_id,                 # The new active subscription
#             'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
#         }
        
#         return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

from flask import request
import jwt
import datetime
from config import JWT_SECRET, get_db_connection

class TokenVerifier:
    
    # =========================================================
    # NEW: Strictly verify if the session still exists in the DB
    # =========================================================
    @staticmethod
    def _is_session_valid(sid):
        if not sid:
            return False
        
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # If the session was deleted by another login, this returns None
            cur.execute("SELECT 1 FROM login.login_sessions WHERE session_id = %s", (sid,))
            result = cur.fetchone()
            return bool(result)
        except Exception as e:
            print(f"Session DB Check Error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_user_id():
        """
        Extracts user_id from the Authorization header.
        Returns: (user_id, error_message)
        """
        token = request.headers.get('Authorization')
        if not token:
            return None, "Missing Authorization Header"

        try:
            if "Bearer" in token:
                token = token.split(" ")[1]
            
            # Decode token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            
            # --- NEW: STRICT 1-DEVICE CHECK ---
            sid = decoded.get('sid')
            if not TokenVerifier._is_session_valid(sid):
                return None, "Session expired. You logged in on another device."
            # ----------------------------------
            
            return decoded.get('sub'), None

        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid Token"
        except Exception as e:
            return None, f"Auth Error: {str(e)}"

    @staticmethod
    def get_user_payload():
        """
        Extracts the FULL payload (claims) from both tokens.
        Returns: dict (payload) or None
        """
        token = request.headers.get('Authorization')
        if not token:
            return None

        try:
            if "Bearer" in token:
                token = token.split(" ")[1]
            
            # 1. Decode main Auth token
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            
            # --- NEW: STRICT 1-DEVICE CHECK ---
            sid = payload.get('sid')
            if not TokenVerifier._is_session_valid(sid):
                print(f"Token rejected: Session {sid} was killed by another login.")
                return None  # Rejects the API call instantly!
            # ----------------------------------

            # 2. Check for Subscription Token and Merge
            sub_token = request.headers.get("Subscription-Token")
            if sub_token:
                try:
                    sub_decoded = jwt.decode(sub_token, JWT_SECRET, algorithms=["HS256"])
                    payload.update(sub_decoded)
                except jwt.ExpiredSignatureError:
                    print("Subscription token expired")
                except jwt.InvalidTokenError:
                    print("Subscription token invalid")

            return payload 

        except Exception as e:
            print(f"Token Error: {str(e)}")
            return None

    @staticmethod
    def verify_admin_tokens():
        """
        Extracts and verifies both auth token and subscription token for admins from headers.
        Returns: (admin_user_id, admin_subscription_id, error_message)
        """
        # 1. Main Auth Token
        user_id_str, auth_error = TokenVerifier.get_user_id()
        if not user_id_str:
            return None, None, auth_error
            
        admin_user_id = int(user_id_str)

        # 2. Subscription Token
        sub_token = request.headers.get('Subscription-Token') or request.headers.get('X-Subscription-Token')
        if not sub_token:
            return admin_user_id, None, "Subscription Token is missing in headers"

        if "Bearer " in sub_token:
            sub_token = sub_token.split(" ")[1]

        if len(sub_token.split('.')) != 3:
            return admin_user_id, None, "FRONTEND ERROR: Pass the long JWT Subscription Token, not the SUB-XXX string."

        try:
            sub_payload = jwt.decode(sub_token, JWT_SECRET, algorithms=["HS256"])
            admin_subscription_id = sub_payload.get("subscription_id") or sub_payload.get("sub_id")
            
            if not admin_subscription_id:
                return admin_user_id, None, "Invalid Subscription Token payload"
                
            return admin_user_id, admin_subscription_id, None

        except jwt.ExpiredSignatureError:
            return admin_user_id, None, "Subscription session expired"
        except jwt.InvalidTokenError:
            return admin_user_id, None, "Invalid Subscription Token"
        except Exception as e:
            return admin_user_id, None, f"Subscription Token Error: {str(e)}"

class TokenGenerator:
    @staticmethod
    def generate_profile_token(user_id, email, mobile, name, username, role_id, roles, sid, sub_id):
        """
        Generates a new JWT specific to the selected Profile.
        """
        payload = {
            'sub': str(user_id),
            'email': email,
            'mobile': mobile,
            'name': name,
            'username': username,
            'role_id': role_id,
            'roles': roles if roles else [],
            'sid': str(sid) if sid else None, 
            'sub_id': sub_id,                 
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256')