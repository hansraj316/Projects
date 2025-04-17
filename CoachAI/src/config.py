"""Configuration management for the CoachAI application."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # OpenAI
    openai_api_key: str = Field(..., env='OPENAI_API_KEY')
    
    # Application
    app_env: str = Field('development', env='APP_ENV')
    debug: bool = Field(True, env='DEBUG')
    host: str = Field('0.0.0.0', env='HOST')
    port: int = Field(8000, env='PORT')
    
    # Vector Store
    vector_store_path: Path = Field(
        Path('./memory/vector_store'),
        env='VECTOR_STORE_PATH'
    )
    
    # Streamlit
    streamlit_port: int = Field(8501, env='STREAMLIT_PORT')
    
    # Logging
    log_level: str = Field('INFO', env='LOG_LEVEL')
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() == 'development'

# Global settings instance
settings = Settings() 