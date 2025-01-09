# app.config.py
# Configuration settings (API keys, DB, etc.).
import os
import logging
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config():
    """Configuration settings for the Healthcare Chatbot application."""

    # General settings
    APP_NAME: str = "HealthCare Chatbot"
    APP_VERSION: str = "1.0"
    DEBUG: bool = str(os.getenv("DEBUG", "False")).lower() == "true"

    # API keys
    GROQ_API_KEY: str = os.getenv('GROQ_API_KEY')
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "mixtral-8x7b-32768")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.7))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 2000))

    # Vector Database settings
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "medical-chatbot")

    # Database settings
    DATABASE_URI: str = os.getenv("DATABASE_URI")

    # Authentication settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    TOKEN_EXPIRATION_MINUTES: int = int(os.getenv("TOKEN_EXPIRATION_MINUTES", 30))

    # File upload settings
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "./uploads")
    ALLOWED_EXTENSIONS: List[str] = ["txt", "pdf"]

    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "app.log"

    def __init__(self):
        """Initialize the configuration settings."""
        self._setup_logging()
        self._ensure_upload_folder()

    def _setup_logging(self):
        """Configure logging based on settings"""
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL.upper()),
            format=self.LOG_FORMAT,
            handlers=[
                logging.FileHandler(self.LOG_FILE),
                logging.StreamHandler()
            ]
        )

    def _ensure_upload_folder(self):
        """Ensure upload folder exists with proper permissions"""
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER, mode=0o755)

# Create an instance of Config to use throughout the app
try:
    config = Config()
    logging.info(f"Configuration loaded successfully for {config.APP_NAME} v{config.APP_VERSION}")
except Exception as e:
    logging.critical(f"Failed to load configuration: {str(e)}")
    raise