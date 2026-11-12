import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-campus-placement-2026-secure-random")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "database" / "placement_system.db"))
    
    # Machine Learning artifact paths
    MODEL_PATH = os.environ.get("MODEL_PATH", str(BASE_DIR / "prediction" / "trained_model.joblib"))
    PREPROCESSOR_PATH = os.environ.get("PREPROCESSOR_PATH", str(BASE_DIR / "prediction" / "preprocessor.joblib"))
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # Set to True if deployed behind HTTPS
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    
    # Upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max request size

class TestingConfig(Config):
    """Configuration used during automated testing."""
    TESTING = True
    SECRET_KEY = "test-secret-key"
    DATABASE_PATH = ":memory:"  # In-memory database for speed and isolation
