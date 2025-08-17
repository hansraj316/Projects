#!/usr/bin/env python3
"""
Test script to verify that critical pages load without errors
"""

import sys
import os
sys.path.insert(0, 'src')

def test_automation_page():
    """Test that automation page components can be imported and initialized"""
    print("Testing Automation Page...")
    
    try:
        from pages.automation import show_automation
        from agents.simple_automation_controller import SimpleAutomationController
        from config import get_config
        
        # Test config loading
        config = get_config()
        print("✅ Config loaded successfully")
        
        # Test controller initialization
        controller = SimpleAutomationController(config.__dict__)
        print("✅ SimpleAutomationController initialized")
        
        # Test required methods exist
        required_methods = [
            'execute_job_automation_workflow',
            'get_automation_history',
            'get_enhanced_workflow_status',
            'get_step_performance_metrics',
            'get_handoff_analytics'
        ]
        
        for method in required_methods:
            if hasattr(controller, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        print("✅ Automation page test passed")
        return True
        
    except Exception as e:
        print(f"❌ Automation page test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_agents_page():
    """Test that AI agents page components can be imported"""
    print("\nTesting AI Agents Page...")
    
    try:
        from pages.ai_agents import show_ai_agents, show_simplified_agent_demo
        from agents.base_agent import AgentTask, AgentContext
        from core.protocols import ILogger, IOpenAIClient, IConfiguration
        
        print("✅ AI agents page imports successful")
        
        # Test protocol runtime checks
        mock_logger = type('MockLogger', (), {
            'debug': lambda self, msg, **kw: None,
            'info': lambda self, msg, **kw: None,
            'warning': lambda self, msg, **kw: None,
            'error': lambda self, msg, **kw: None,
            'critical': lambda self, msg, **kw: None
        })()
        
        # This should work now with @runtime_checkable
        is_logger = isinstance(mock_logger, ILogger)
        print(f"✅ Protocol runtime check works: {is_logger}")
        
        # Test agent task creation
        task = AgentTask(
            task_type="test",
            description="Test task"
        )
        context = AgentContext(user_id="test_user")
        print("✅ AgentTask and AgentContext created successfully")
        
        print("✅ AI agents page test passed")
        return True
        
    except Exception as e:
        print(f"❌ AI agents page test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_other_critical_pages():
    """Test other critical pages for basic import issues"""
    print("\nTesting Other Critical Pages...")
    
    pages_to_test = [
        'pages.dashboard',
        'pages.resume_manager',
        'pages.job_search',
        'pages.applications',
        'pages.notifications',
        'pages.settings'
    ]
    
    results = []
    
    for page in pages_to_test:
        try:
            __import__(page)
            print(f"✅ {page} imports successfully")
            results.append(True)
        except Exception as e:
            print(f"❌ {page} import failed: {e}")
            results.append(False)
    
    return all(results)

def main():
    """Run all tests"""
    print("🧪 InterviewAgent Page Tests")
    print("=" * 40)
    
    results = []
    
    # Test automation page (critical)
    results.append(test_automation_page())
    
    # Test AI agents page (critical)
    results.append(test_ai_agents_page())
    
    # Test other pages (less critical)
    results.append(test_other_critical_pages())
    
    print("\n" + "=" * 40)
    if all(results):
        print("🎉 All tests passed! Pages should load correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    exit(main())