import os
import base64
import shutil
from flask import request, current_app
from werkzeug.utils import secure_filename
from utils.token_helper import TokenVerifier
from utils.api_response import api_response

# Define allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_storage_path(user_id, subscription_id=None):
    """
    Constructs path based on requirement:
    1. If Sub ID: uploads/profile_images/{user_id}/{subscription_id}/{user_id}.png
    2. No Sub ID: uploads/profile_images/{user_id}/{user_id}.png
    """
    base_uploads = os.path.join(current_app.root_path, 'uploads', 'profile_images')
    
    # Filename is ALWAYS {user_id}.png as requested
    filename = f"{user_id}.png"

    if subscription_id:
        # Clean sub_id to avoid path traversal issues
        safe_sub_id = secure_filename(subscription_id)
        # Folder: uploads/profile_images/107/SUB-2026.../
        folder_path = os.path.join(base_uploads, str(user_id), safe_sub_id)
    else:
        # Folder: uploads/profile_images/107/
        folder_path = os.path.join(base_uploads, str(user_id))
        
    return folder_path, filename

def upload_profile_image():
    """
    POST /api/v1/user/profile-image/upload
    """
    try:
        # 1. Get User Payload
        payload = TokenVerifier.get_user_payload()
        if not payload:
            return api_response(message="Unauthorized", code=401, status="error")
        
        user_id = str(payload.get('sub'))
        roles = payload.get('roles', [])

        # 2. Extract Subscription ID
        subscription_id = None
        for role in roles:
            if role.get('is_default') is True:
                subscription_id = role.get('subscription_id')
                break
        
        if not subscription_id:
             subscription_id = payload.get('sub_id')

        # 3. Validation
        if 'file' not in request.files:
            return api_response(message="No file part", code=400, status="error")
        
        file = request.files['file']
        if file.filename == '':
            return api_response(message="No selected file", code=400, status="error")

        if file and allowed_file(file.filename):
            # 4. Get Path
            folder_path, filename = get_storage_path(user_id, subscription_id)
            
            # Create recursive directories (e.g., .../107/SUB-123/)
            os.makedirs(folder_path, exist_ok=True)
            
            file_path = os.path.join(folder_path, filename)

            # 5. Save (This automatically overwrites if it exists)
            file.save(file_path)

            return api_response(message="Profile image uploaded successfully", code=200, status="success")
        
        else:
            return api_response(message="Invalid file type. Allowed: png, jpg, jpeg", code=400, status="error")

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")

def get_profile_image():
    """
    GET /api/v1/user/profile-image
    """
    try:
        # 1. Get User Payload
        payload = TokenVerifier.get_user_payload()
        if not payload:
            return api_response(message="Unauthorized", code=401, status="error")
            
        user_id = str(payload.get('sub'))
        roles = payload.get('roles', [])

        # 2. Extract Subscription ID
        subscription_id = None
        for role in roles:
            if role.get('is_default') is True:
                subscription_id = role.get('subscription_id')
                break
        
        if not subscription_id:
             subscription_id = payload.get('sub_id')

        # 3. Determine Paths
        # Path A: Specific Subscription Image (.../107/SUB-123/107.png)
        sub_folder, sub_filename = get_storage_path(user_id, subscription_id)
        sub_file_path = os.path.join(sub_folder, sub_filename)
        
        # Path B: Generic User Image (.../107/107.png)
        # Note: We pass None to get the non-subscription path
        def_folder, def_filename = get_storage_path(user_id, None) 
        def_file_path = os.path.join(def_folder, def_filename)

        final_path = None

        # 4. Check Existence (Priority: Subscription > Global)
        if os.path.exists(sub_file_path):
            final_path = sub_file_path
        elif os.path.exists(def_file_path):
            final_path = def_file_path
        else:
            return api_response(message="Profile image not found", code=404, status="error")

        # 5. Return Base64
        with open(final_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        base64_image = f"data:image/png;base64,{encoded_string}"

        return api_response(
            message="Image retrieved successfully", 
            data={"image": base64_image}, 
            code=200, 
            status="success"
        )

    except Exception as e:
        return api_response(message="Server Error", error=str(e), code=500, status="error")