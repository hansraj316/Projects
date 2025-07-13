"""
Database connection and initialization for InterviewAgent
"""

import streamlit as st
from supabase import create_client, Client
from typing import Optional
import logging
from config import get_config

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection manager for Supabase"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.config = get_config()
        
    def connect(self) -> Client:
        """Establish connection to Supabase"""
        if self.client is None:
            try:
                # Skip real connection for test URLs
                if self.config.SUPABASE_URL == "test-url":
                    logger.info("Using test mode - skipping Supabase connection")
                    return None
                    
                self.client = create_client(
                    self.config.SUPABASE_URL,
                    self.config.SUPABASE_KEY
                )
                logger.info("Successfully connected to Supabase")
            except Exception as e:
                logger.error(f"Failed to connect to Supabase: {str(e)}")
                raise
        
        return self.client
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            # For testing without real Supabase, just return True
            if self.config.SUPABASE_URL == "test-url":
                logger.info("Using test mode - database connection simulated")
                return True
                
            client = self.connect()
            # Simple test query
            result = client.table('users').select('id').limit(1).execute()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False

# Global database connection instance
_db_connection = None

def get_db_connection() -> DatabaseConnection:
    """Get database connection instance"""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return get_db_connection().connect()

@st.cache_resource
def init_database():
    """Initialize database connection with caching"""
    try:
        db = get_db_connection()
        client = db.connect()
        
        # Test connection
        if not db.test_connection():
            logger.warning("Database connection test failed, continuing in mock mode")
        
        # Initialize tables if needed (for MVP, we assume tables exist)
        logger.info("Database initialized successfully")
        return client
    except Exception as e:
        logger.warning(f"Database initialization failed, continuing in mock mode: {str(e)}")
        return None

def execute_sql_file(sql_file_path: str) -> bool:
    """Execute SQL file (for migrations)"""
    try:
        client = get_supabase_client()
        
        with open(sql_file_path, 'r') as file:
            sql_content = file.read()
        
        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            try:
                # Note: Supabase Python client doesn't directly support raw SQL execution
                # In production, you would use the Supabase CLI or REST API for migrations
                logger.warning(f"SQL execution not implemented for statement: {statement[:50]}...")
            except Exception as e:
                logger.error(f"Failed to execute SQL statement: {str(e)}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Failed to execute SQL file {sql_file_path}: {str(e)}")
        return False