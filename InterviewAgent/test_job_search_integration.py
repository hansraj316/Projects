#!/usr/bin/env python3
"""
Integration test for job search functionality using OpenAI Responses API
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.job_discovery import JobDiscoveryAgent
from agents.base_agent import AgentTask, AgentContext
from config import Config
from database.operations import get_db_operations


class TestLogger:
    """Simple test logger"""
    def info(self, message, **kwargs):
        print(f"ℹ️  {message}")
        
    def warning(self, message, **kwargs):
        print(f"⚠️  {message}")
        
    def error(self, message, **kwargs):
        print(f"❌ {message}")


async def test_job_search_integration():
    """Test the complete job search integration"""
    
    print("🧪 Testing Job Search Integration with OpenAI Responses API")
    print("=" * 60)
    
    # Initialize configuration
    try:
        config = Config()
        print(f"✅ Configuration loaded")
        print(f"   - OpenAI API Key: {'*' * 20 if config.OPENAI_API_KEY else 'Not configured'}")
        print(f"   - Model: {getattr(config, 'OPENAI_MODEL', 'Default')}")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return
    
    # Test database connection
    try:
        db_ops = get_db_operations()
        user = db_ops.get_or_create_user(
            email="test@interviewagent.local",
            full_name="Test User"
        )
        print(f"✅ Database connection successful")
        print(f"   - User ID: {user.id}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Initialize job discovery agent
    try:
        agent = JobDiscoveryAgent(
            name="job_discovery_test",
            description="AI-powered job discovery agent for testing",
            logger=TestLogger(),
            openai_client=config.get_openai_client(),
            config=config
        )
        print(f"✅ Job Discovery Agent initialized")
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return
    
    # Test different search scenarios
    test_scenarios = [
        {
            "name": "Software Engineer in San Francisco",
            "job_title": "Software Engineer",
            "location": "San Francisco",
            "experience_level": "Mid Level"
        },
        {
            "name": "Remote Python Developer",
            "job_title": "Python Developer", 
            "location": "",
            "experience_level": "Senior",
            "remote_preference": "Remote"
        },
        {
            "name": "Data Scientist in New York",
            "job_title": "Data Scientist",
            "location": "New York",
            "experience_level": "Entry Level"
        }
    ]
    
    print(f"\n🔍 Running {len(test_scenarios)} search scenarios...")
    print("-" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📊 Scenario {i}: {scenario['name']}")
        
        # Create task
        task = AgentTask(
            task_id=f"test_{i}_{datetime.now().strftime('%H%M%S')}",
            task_type="search_jobs",
            description=f"Test search for {scenario['job_title']}",
            input_data=scenario
        )
        
        # Create context
        context = AgentContext(
            user_id=user.id,
            metadata={
                "test_scenario": i,
                "scenario_name": scenario['name']
            }
        )
        
        try:
            # Execute search
            print(f"   🔄 Searching...")
            result = await agent.execute(task, context)
            
            if result.success:
                jobs = result.data.get('jobs', [])
                search_query = result.data.get('search_query', 'Unknown')
                
                print(f"   ✅ Search successful!")
                print(f"   📋 Jobs found: {len(jobs)}")
                print(f"   🔎 Search query used: {search_query}")
                
                if jobs:
                    # Show sample job details
                    sample_job = jobs[0]
                    print(f"   📄 Sample job:")
                    print(f"      • Title: {sample_job.get('title', 'N/A')}")
                    print(f"      • Company: {sample_job.get('company', 'N/A')}")
                    print(f"      • Location: {sample_job.get('location', 'N/A')}")
                    print(f"      • URL: {sample_job.get('job_url', 'N/A')}")
                    print(f"      • Source: {sample_job.get('source', 'N/A')}")
                
                # Test saving to database
                try:
                    search_criteria = {k: v for k, v in scenario.items() if k != 'name'}
                    job_search = db_ops.create_job_search(
                        user_id=user.id,
                        search_query=search_query,
                        search_criteria=search_criteria,
                        jobs_found=len(jobs),
                        search_results=result.data
                    )
                    print(f"   💾 Search saved to database (ID: {job_search.id})")
                except Exception as e:
                    print(f"   ⚠️  Database save failed: {e}")
                    
            else:
                print(f"   ❌ Search failed: {result.error}")
                
        except Exception as e:
            print(f"   💥 Scenario failed: {e}")
    
    print(f"\n📈 Integration Test Summary")
    print("=" * 60)
    
    # Get final database stats
    try:
        recent_searches = db_ops.get_job_searches(user.id, limit=10)
        print(f"✅ Total searches in database: {len(recent_searches)}")
        
        total_jobs = sum(search.jobs_found or 0 for search in recent_searches)
        print(f"✅ Total jobs found across all searches: {total_jobs}")
        
        if recent_searches:
            latest = recent_searches[0]
            print(f"✅ Latest search: '{latest.search_query}' found {latest.jobs_found} jobs")
            
    except Exception as e:
        print(f"❌ Database stats failed: {e}")
    
    print("\n🎉 Integration test completed!")


if __name__ == "__main__":
    asyncio.run(test_job_search_integration())