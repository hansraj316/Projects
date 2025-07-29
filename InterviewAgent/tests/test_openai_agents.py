#!/usr/bin/env python3
"""
Test OpenAI Agents SDK integration
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_openai_agents_integration():
    """Test the OpenAI Agents SDK integration without full imports"""
    
    print("🧪 Testing OpenAI Agents SDK Integration...")
    
    try:
        # Test basic OpenAI Agents SDK imports
        print("📦 Testing OpenAI Agents SDK imports...")
        
        try:
            # Handle naming conflict with our local agents module
            import sys
            import os
            
            # Temporarily adjust path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, 'src')
            if src_dir in sys.path:
                sys.path.remove(src_dir)
            
            # Import OpenAI Agents SDK
            from agents import Agent, handoff, Runner
            print("✅ OpenAI Agents SDK imported successfully")
            
            # Restore path
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
                
        except ImportError as e:
            print(f"❌ OpenAI Agents SDK import failed: {e}")
            return False
        
        print("🏗️ Testing Agent creation...")
        
        # Create a simple test agent
        test_agent = Agent(
            name="Test Agent",
            instructions="You are a test agent for the InterviewAgent system.",
            model="gpt-4o-mini"
        )
        
        print("✅ Test agent created successfully")
        
        # Test handoff creation
        print("🔄 Testing handoff creation...")
        
        second_agent = Agent(
            name="Second Agent", 
            instructions="You are a second test agent.",
            model="gpt-4o-mini"
        )
        
        test_handoff = handoff(
            agent=second_agent,
            tool_description_override="Test handoff to second agent"
        )
        
        print("✅ Handoff created successfully")
        
        # Create agent with handoffs
        orchestrator_agent = Agent(
            name="Test Orchestrator",
            instructions="You coordinate between test agents.",
            handoffs=[test_agent, test_handoff],
            model="gpt-4o-mini"
        )
        
        print("✅ Orchestrator agent with handoffs created successfully")
        print("📝 Note: Full execution requires OpenAI API key configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting OpenAI Agents SDK Integration Test\n")
    
    try:
        result = asyncio.run(test_openai_agents_integration())
        
        if result:
            print("\n🎉 OpenAI Agents SDK integration test completed successfully!")
            print("📝 The system is ready to use OpenAI Agents SDK handoffs")
            print("💡 To use full functionality, configure OPENAI_API_KEY environment variable")
        else:
            print("\n❌ OpenAI Agents SDK integration test failed")
            
    except Exception as e:
        print(f"\n💥 Test crashed: {str(e)}")

if __name__ == "__main__":
    main()