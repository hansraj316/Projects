"""
Logging utilities for InterviewAgent
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from config import get_config

def setup_logging(log_level: str = "INFO"):
    """Setup application logging"""
    
    config = get_config()
    
    # Create logs directory
    logs_dir = Path(config.LOGS_DIR)
    logs_dir.mkdir(exist_ok=True)
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler
    log_file = logs_dir / f"interview_agent_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler (only for development)
    if config.DEBUG:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger('supabase').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    logging.info("Logging setup completed")

class AgentLogger:
    """Specialized logger for AI agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")
    
    def log_start(self, action: str, context: dict = None):
        """Log agent action start"""
        msg = f"Started action: {action}"
        if context:
            msg += f" with context: {context}"
        self.logger.info(msg)
    
    def log_success(self, action: str, result: dict = None, duration_ms: int = None):
        """Log agent action success"""
        msg = f"Completed action: {action}"
        if duration_ms:
            msg += f" in {duration_ms}ms"
        if result:
            msg += f" with result: {result}"
        self.logger.info(msg)
    
    def log_error(self, action: str, error: str, context: dict = None):
        """Log agent action error"""
        msg = f"Failed action: {action} - Error: {error}"
        if context:
            msg += f" - Context: {context}"
        self.logger.error(msg)
    
    def log_warning(self, action: str, warning: str):
        """Log agent warning"""
        msg = f"Warning in action: {action} - {warning}"
        self.logger.warning(msg)

def get_agent_logger(agent_name: str) -> AgentLogger:
    """Get agent logger instance"""
    return AgentLogger(agent_name)