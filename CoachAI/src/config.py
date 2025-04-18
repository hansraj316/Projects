"""Configuration settings for the application."""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    app_env: str = "development"
    debug: bool = True
    streamlit_port: int = 8501

settings = Settings() 