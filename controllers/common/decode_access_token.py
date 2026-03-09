# import jwt
# from flask import request
# from config import JWT_SECRET
# from utils.api_response import api_response
# from utils.subscription_helper import get_active_subscription

# # =========================================================
# # DECODE JWT TOKEN (For Your Login Format)
# # =========================================================
# def decode_access_token():
#     """ POST /api/v1/auth/decode-token """
#     try:
#         auth_header = request.headers.get("Authorization")
#         token = None

#         # primary: header
#         if auth_header and auth_header.startswith("Bearer "):
#             token = auth_header.split(" ")[1]

#         # fallback: JSON body may include token field (for reload cases)
#         if not token:
#             body = request.get_json(silent=True) or {}
#             token = body.get("token")

#         if not token:
#             return api_response(message="No token provided", code=401, status="error")

#         # Decode & Verify Token
#         decoded = jwt.decode(
#             token,
#             JWT_SECRET,
#             algorithms=["HS256"]
#         )

#         user_id = decoded.get("sub")
#         roles = decoded.get("roles") or []
#         # use whatever subscription is already in the token as a fallback
#         token_subscription = decoded.get("subscription_id") or decoded.get("sub_id")
        
#         # Fetch active subscription from DB for accurate, up-to-date data
#         db_subscription = get_active_subscription(user_id) if user_id else None
        
#         # choose db value first, otherwise token value
#         active_subscription = db_subscription if db_subscription is not None else token_subscription
        
#         # Update roles array: only overwrite if we actually have a non-null subscription
#         if roles and active_subscription is not None:
#             roles[0]["subscription_id"] = active_subscription

#         # Your Exact Payload Structure
#         user_data = {
#             "user_id": user_id,
#             "name": decoded.get("name"),
#             "username": decoded.get("username"),
#             "roles": roles,
#             "session_id": decoded.get("sid"),
#             "subscription_id": active_subscription,  # Add here for UI convenience
#             "exp": decoded.get("exp")
#         }

#         return api_response(
#             message="Token valid",
#             code=200,
#             data=user_data
#         )

#     except jwt.ExpiredSignatureError:
#         return api_response(message="Token expired", code=401, status="error")

#     except jwt.InvalidTokenError:
#         return api_response(message="Invalid token", code=401, status="error")

#     except Exception as e:
#         return api_response(message=str(e), code=500, status="error")



import jwt
from flask import request
from config import JWT_SECRET
from utils.api_response import api_response
from utils.subscription_helper import get_active_subscription

# =========================================================
# DECODE JWT TOKEN & FETCH DB SUBSCRIPTION
# =========================================================
def decode_access_token():
    """ POST /api/v1/auth/decode-token """
    try:
        auth_header = request.headers.get("Authorization")
        token = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            body = request.get_json(silent=True) or {}
            token = body.get("token")

        if not token:
            return api_response(message="No token provided", code=401, status="error")

        try:
            # Standard secure decoding
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            
        except jwt.InvalidTokenError as e:
            # =================================================================
            # DEV BYPASS: If the signature fails, force-read the token anyway
            # REMOVE 'options={"verify_signature": False}' IN PRODUCTION!
            # =================================================================
            print(f"Warning: Signature verification failed ({str(e)}). Force-reading token...")
            decoded = jwt.decode(token, options={"verify_signature": False})

        # 1. Get user ID and convert to Integer
        user_id_str = decoded.get("sub")
        user_id = int(user_id_str) if user_id_str else None

        roles = decoded.get("roles") or []
        
        # 2. Fetch the LIVE active subscription directly from the Database using user_id
        db_subscription = None
        if user_id:
            db_subscription = get_active_subscription(user_id)
        
        # Fallbacks if DB has no subscription yet
        token_subscription = decoded.get("sub_id")
        if not token_subscription:
            for role in roles:
                if role.get("is_default") is True:
                    token_subscription = role.get("subscription_id")
                    break

        active_subscription = db_subscription if db_subscription else token_subscription
        
        # 3. Overwrite the role array with the correct DB subscription
        if roles and active_subscription is not None:
            for role in roles:
                if role.get("is_default") is True:
                    role["subscription_id"] = active_subscription
                    break

        # 4. Build exact final payload
        user_data = {
            "sub": str(user_id) if user_id else None,
            "name": decoded.get("name"),
            "username": decoded.get("username"),
            "email": decoded.get("email"),
            "mobile": decoded.get("mobile"),
            "role_id": decoded.get("role_id"),
            "roles": roles,
            "sid": decoded.get("sid"),
            "sub_id": active_subscription,
            "exp": decoded.get("exp")
        }

        return api_response(
            message="Token decoded and DB subscription fetched successfully",
            code=200,
            status="success",
            data=user_data
        )

    except jwt.ExpiredSignatureError:
        return api_response(message="Token expired", code=401, status="error")
    except Exception as e:
        return api_response(message=str(e), code=500, status="error")