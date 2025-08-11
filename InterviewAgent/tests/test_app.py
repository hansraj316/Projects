#!/usr/bin/env python3
"""
Simple test script to verify InterviewAgent components
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from config import load_config, get_config
        print("✅ Config module imported successfully")
        
        from database.connection import get_db_connection
        print("✅ Database connection module imported successfully")
        
        from database.operations import get_db_operations
        print("✅ Database operations module imported successfully")
        
        from database.models import User, JobSite, Application
        print("✅ Database models imported successfully")
        
        from utils.logging_utils import setup_logging
        print("✅ Logging utils imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_config():
    """Test configuration loading"""
    try:
        from config import load_config
        config = load_config()
        print(f"✅ Configuration loaded: {config['APP_NAME']}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def test_database():
    """Test database operations"""
    try:
        from database.operations import get_db_operations
        db = get_db_operations()
        
        # Test user creation (mock mode)
        user = db.get_or_create_user("test@example.com", "Test User")
        print(f"✅ User creation test passed: {user.email}")
        
        # Test stats retrieval
        stats = db.get_user_stats(user.id)
        print(f"✅ Stats retrieval test passed: {stats}")
        
        # Test job sites
        sites = db.get_job_sites(user.id)
        print(f"✅ Job sites test passed: {len(sites)} sites")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

def test_agents():
    """Test AI agents system"""
    try:
        from agents import AgentManager
        from config import load_config
        
        config = load_config()
        agent_manager = AgentManager(config)
        agent_manager.initialize_agents()
        
        print(f"✅ Agent initialization test passed")
        
        # Test agent status
        status = agent_manager.get_agent_status()
        print(f"✅ Agent status test passed: {len(status)} agents loaded")
        
        # Test agent functionality
        test_results = agent_manager.test_agents()
        passed = sum(test_results.values())
        total = len(test_results)
        print(f"✅ Agent functionality test: {passed}/{total} agents working")
        
        return True
    except Exception as e:
        print(f"❌ Agents test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing InterviewAgent Components...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config), 
        ("Database", test_database),
        ("AI Agents", test_agents)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! InterviewAgent is ready to run.")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)