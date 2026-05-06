from routes.student_route import register_student_routes
from routes.admin_route import register_admin_routes
from routes.teacher_route import register_teacher_routes
from routes.users_route import register_user_routes
from routes.auth_route import register_auth_routes
from routes.blogs_route import register_blog_routes
import os
import logging
from flask import Flask
from flask_cors import CORS
from config import get_db_connection


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#  register routes properly
register_blog_routes(app)
register_auth_routes(app)
register_user_routes(app)
register_teacher_routes(app)
register_admin_routes(app)
register_student_routes(app)

@app.route("/")
def health():
    return "API is running"


if __name__ == "__main__":
    get_db_connection().close()
    port = int(os.environ.get("PORT", 8000))
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    print(f"Server running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
