#!/usr/bin/env python3
"""
Test script to check Supabase integration status
"""

import sys
import os
sys.path.append('src')

from database.connection import get_db_connection, init_database
from database.operations import get_db_operations
from config import Config

def test_supabase_integration():
    """Test Supabase integration"""
    print("🔍 Testing Supabase Integration")
    print("=" * 50)
    
    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    config = Config()
    print(f"   ✓ SUPABASE_URL: {config.SUPABASE_URL}")
    print(f"   ✓ SUPABASE_KEY: {'*' * 10 if config.SUPABASE_KEY else 'NOT SET'}")
    
    if config.SUPABASE_URL == "test-url":
        print("   ⚠️  Currently using test configuration")
        print("   💡 To use real Supabase, update your .env file with:")
        print("      SUPABASE_URL=https://your-project.supabase.co")
        print("      SUPABASE_KEY=your-anon-key")
    
    # Test 2: Database Connection
    print("\n2. Testing Database Connection...")
    try:
        db_conn = get_db_connection()
        client = init_database()
        
        if client is None:
            print("   ⚠️  Running in mock mode (no real database connection)")
            print("   💡 This is expected with test configuration")
        else:
            print("   ✓ Database connection successful!")
            
        # Test connection
        connection_ok = db_conn.test_connection()
        print(f"   ✓ Connection test: {'PASS' if connection_ok else 'FAIL'}")
        
    except Exception as e:
        print(f"   ❌ Connection error: {str(e)}")
    
    # Test 3: Database Operations
    print("\n3. Testing Database Operations...")
    try:
        db_ops = get_db_operations()
        
        # Test user operations
        user = db_ops.get_or_create_user("test@example.com", "Test User")
        print(f"   ✓ User creation: {user.email}")
        
        # Test stats
        stats = db_ops.get_user_stats(user.id)
        print(f"   ✓ User stats: {stats}")
        
        # Test job sites
        job_sites = db_ops.get_job_sites(user.id)
        print(f"   ✓ Job sites: {len(job_sites)} sites available")
        
        # Test agent logs
        agent_logs = db_ops.get_agent_logs(user.id)
        print(f"   ✓ Agent logs: {len(agent_logs)} logs available")
        
    except Exception as e:
        print(f"   ❌ Database operations error: {str(e)}")
    
    # Test 4: Agent Result Storage
    print("\n4. Testing Agent Result Storage...")
    try:
        # Test agent result creation
        agent_result = db_ops.create_agent_result(
            user_id=user.id,
            agent_type="test_agent",
            task_type="test_task",
            input_data={"test": "input"},
            output_data={"test": "output"},
            success=True
        )
        print(f"   ✓ Agent result created: {agent_result.id}")
        
        # Test cover letter storage
        cover_letter = db_ops.create_cover_letter(
            user_id=user.id,
            job_title="Software Engineer",
            company_name="Test Company",
            cover_letter_content="Test cover letter content",
            quality_score=85
        )
        print(f"   ✓ Cover letter stored: {cover_letter.id}")
        
        # First create a resume template for testing
        import uuid
        resume_template = db_ops.create_resume_template(
            user_id=user.id,
            name="Test Resume",
            content="Test resume content"
        )
        
        # Test optimized resume storage
        optimized_resume = db_ops.create_optimized_resume(
            user_id=user.id,
            original_resume_id=resume_template.id,
            job_title="Software Engineer",
            company_name="Test Company",
            optimized_content="Optimized resume content",
            job_match_score=90
        )
        print(f"   ✓ Optimized resume stored: {optimized_resume.id}")
        
    except Exception as e:
        print(f"   ❌ Agent result storage error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Supabase Integration Test Complete!")
    
    if config.SUPABASE_URL == "test-url":
        print("\n🔧 Next Steps to Enable Real Supabase:")
        print("1. Create a Supabase project at https://supabase.com")
        print("2. Get your project URL and anon key from Settings > API")
        print("3. Update your .env file:")
        print("   SUPABASE_URL=https://your-project.supabase.co")
        print("   SUPABASE_KEY=your-anon-key")
        print("4. Run the migrations in Supabase SQL editor:")
        print("   - Execute src/database/migrations.sql")
        print("   - Execute src/database/agent_migrations.sql")
        print("5. Restart the application")

if __name__ == "__main__":
    test_supabase_integration()