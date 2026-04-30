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


@app.route("/")
def health():
    return "API is running"


def check_db_connection():
    conn = None
    try:
        conn = get_db_connection()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f" Database connection failed: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    check_db_connection()
    port = int(os.environ.get("PORT", 8000))
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    print(f"Server running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
