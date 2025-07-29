"""
InterviewAgent - AI-powered job application automation system

Production-ready architecture with dependency injection, security, and error handling.
"""

__version__ = "1.0.0"
__author__ = "InterviewAgent Team"

# Core components
from .core.bootstrap import create_application, initialize_application, get_application_info
from .core.container import get_container
from .config import get_config, AppConfig

# Main application entry points
__all__ = [
    "create_application",
    "initialize_application", 
    "get_application_info",
    "get_container",
    "get_config",
    "AppConfig"
]