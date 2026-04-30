import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import sys
import logging

sys.dont_write_bytecode = True

# Load .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

HOST_URL = os.getenv("HOST_URL")

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        conn.autocommit = True
        logger.info("Database connected successfully")
        return conn
    except Exception as e:
        logger.error(f" Database connection failed: {e}")
        raise e
