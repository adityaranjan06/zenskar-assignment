# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file at startup

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
