# # utils/token_helper.py
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
#         # base payload with identity fields
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

# utils/token_helper.py
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

# utils/token_helper.py
from flask import request
import jwt
import datetime
from config import JWT_SECRET

class TokenVerifier:
    @staticmethod
    def get_user_id():
        """
        Extracts user_id from the Authorization header in the global Flask request object.
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
            return decoded.get('sub'), None

        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid Token"
        except Exception as e:
            return None, f"Auth Error: {str(e)}"

    @staticmethod
    def get_subscription_id():
        """
        Extracts the subscription_id from the new 'x-subscription-token' header.
        """
        sub_token = request.headers.get('x-subscription-token')
        if not sub_token:
            return None

        try:
            # Decode the separate subscription token
            decoded = jwt.decode(sub_token, JWT_SECRET, algorithms=["HS256"])
            return decoded.get('subscription_id')
        except Exception as e:
            print(f"Subscription Token Error: {str(e)}")
            return None

    @staticmethod
    def get_user_payload():
        """
        Extracts the FULL payload (claims) from the auth token.
        Automatically merges the subscription_id from the secondary header 
        so existing Dashboard APIs don't break!
        """
        token = request.headers.get('Authorization')
        if not token:
            return None

        try:
            if "Bearer" in token:
                token = token.split(" ")[1]
            
            # Decode main auth token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            
            # Extract subscription ID from the secondary header
            sub_id = TokenVerifier.get_subscription_id()
            if sub_id:
                decoded['subscription_id'] = sub_id
                decoded['sub_id'] = sub_id
                
            return decoded 

        except Exception as e:
            print(f"Token Error: {str(e)}")
            return None


class TokenGenerator:
    @staticmethod
    def generate_profile_token(user_id, email, mobile, name, username, role_id, roles, sid):
        """
        Generates a new Auth JWT. 
        Notice: sub_id has been completely removed from this payload!
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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

    @staticmethod
    def generate_subscription_token(subscription_id):
        """
        Generates a dedicated JWT solely for the subscription ID.
        """
        payload = {
            'subscription_id': subscription_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256')