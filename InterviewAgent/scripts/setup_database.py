#!/usr/bin/env python3
"""
Setup script to create database tables in Supabase
"""

import sys
import os
sys.path.append('src')

from database.connection import get_supabase_client
from config import Config

def setup_database():
    """Create database tables using Supabase REST API"""
    print("🔧 Setting up Supabase Database")
    print("=" * 50)
    
    config = Config()
    
    if config.SUPABASE_URL == "test-url":
        print("❌ Cannot setup database with test configuration")
        print("Please update your .env file with real Supabase credentials")
        return False
    
    try:
        client = get_supabase_client()
        
        # Since we can't execute raw SQL with the Python client, 
        # we'll provide instructions for manual setup
        print("\n📝 Database Setup Instructions:")
        print("=" * 30)
        print("1. Go to your Supabase project dashboard:")
        print(f"   {config.SUPABASE_URL.replace('https://', 'https://').replace('.supabase.co', '.supabase.co/project/')}")
        print("\n2. Navigate to 'SQL Editor' in the left sidebar")
        print("\n3. Create a new query and paste the contents of:")
        print("   📄 src/database/migrations.sql")
        print("   📄 src/database/agent_migrations.sql")
        print("\n4. Run each migration file separately")
        
        print("\n🎯 Quick Setup Option:")
        print("Copy and paste this complete SQL script into Supabase SQL Editor:")
        print("=" * 60)
        
        # Read and combine migration files
        try:
            with open('src/database/migrations.sql', 'r') as f:
                main_migrations = f.read()
            
            with open('src/database/agent_migrations.sql', 'r') as f:
                agent_migrations = f.read()
            
            combined_sql = f"""-- InterviewAgent Complete Database Setup
-- Run this script in Supabase SQL Editor

{main_migrations}

-- Agent-specific tables
{agent_migrations}

-- Verify tables were created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'resume_templates', 'job_sites', 'job_listings', 'applications', 'schedules', 'agent_logs', 'agent_results', 'cover_letters', 'optimized_resumes', 'job_searches')
ORDER BY table_name;
"""
            
            print(combined_sql)
            
        except FileNotFoundError as e:
            print(f"❌ Migration file not found: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("After running the SQL script, test the connection again with:")
        print("python3 test_supabase.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup error: {str(e)}")
        return False

if __name__ == "__main__":
    setup_database()