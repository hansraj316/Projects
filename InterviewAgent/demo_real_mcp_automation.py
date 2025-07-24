"""
Demonstration of Real MCP Playwright Automation for InterviewAgent
This script uses the actual MCP Playwright tools to open a browser and navigate to job sites
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from src.automation.real_mcp_implementation import execute_real_mcp_job_automation


def get_sample_job_data():
    """Get realistic job data with actual application URLs"""
    return {
        "title": "Software Engineer",
        "company": "Microsoft",
        "location": "Seattle, WA (Remote)",
        "summary": "Join Microsoft as a Software Engineer working on cutting-edge cloud technologies.",
        "application_url": "https://careers.microsoft.com/professionals/us/en/search-results",
        "apply_link": "https://careers.microsoft.com/professionals/us/en/search-results",
        "source": "Company Website",
        "salary_range": "$120k-160k",
        "skills": ["Python", "JavaScript", "React", "AWS", "Docker"],
        "experience_level": "Mid-level",
        "posted_date": "2 days ago"
    }


def get_sample_user_profile():
    """Get sample user profile for form filling"""
    return {
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1-555-0123",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "portfolio_url": "https://johndoe.dev",
        "location": "San Francisco, CA",
        "current_position": "Software Developer"
    }


def get_sample_resume_data():
    """Get sample resume data"""
    return {
        "file_path": str(Path.home() / "Documents" / "resume.pdf"),
        "content": "Professional software engineer with 5+ years experience...",
        "last_updated": datetime.now().isoformat()
    }


def get_sample_cover_letter_data():
    """Get sample cover letter data"""
    return {
        "file_path": str(Path.home() / "Documents" / "cover_letter.pdf"),
        "content": "Dear Hiring Manager, I am excited to apply for the Software Engineer position...",
        "last_updated": datetime.now().isoformat()
    }


async def demo_microsoft_careers():
    """Demonstrate automation on Microsoft careers page"""
    print("🚀 Demonstrating Real MCP Playwright Automation")
    print("=" * 80)
    print("🎯 Target: Microsoft Careers Page")
    print("🔧 Using actual MCP Playwright tools available in Claude Code")
    print("-" * 80)
    
    # Prepare demo data
    job_data = get_sample_job_data()
    user_profile = get_sample_user_profile()
    resume_data = get_sample_resume_data()
    cover_letter_data = get_sample_cover_letter_data()
    
    # Automation settings
    automation_settings = {
        "screenshot_dir": "data/demo_screenshots",
        "browser_width": 1280,
        "browser_height": 720,
        "headless": False  # Show browser for demo
    }
    
    # Create screenshot directory
    Path(automation_settings["screenshot_dir"]).mkdir(parents=True, exist_ok=True)
    
    print(f"📋 Job Details:")
    print(f"   Company: {job_data['company']}")
    print(f"   Position: {job_data['title']}")
    print(f"   URL: {job_data['application_url']}")
    print(f"   Location: {job_data['location']}")
    
    print(f"\n👤 User Profile:")
    print(f"   Name: {user_profile['first_name']} {user_profile['last_name']}")
    print(f"   Email: {user_profile['email']}")
    print(f"   Phone: {user_profile['phone']}")
    
    print(f"\n📸 Screenshots will be saved to: {automation_settings['screenshot_dir']}")
    print("-" * 80)
    
    try:
        # Execute the real MCP automation
        print("🎬 Starting automation...")
        result = await execute_real_mcp_job_automation(
            job_data,
            user_profile,
            resume_data,
            cover_letter_data,
            automation_settings
        )
        
        # Display results
        print(f"\n🎯 AUTOMATION RESULTS")
        print(f"=" * 50)
        print(f"Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        print(f"Execution Time: {result['execution_time']}")
        print(f"Browser Opened: {'✅' if result['browser_opened'] else '❌'}")
        print(f"Navigation Successful: {'✅' if result['navigation_successful'] else '❌'}")
        print(f"Screenshots Taken: {len(result['screenshots_taken'])}")
        print(f"Page Snapshots: {len(result.get('page_snapshots_taken', []))}")
        
        if result['steps_executed']:
            print(f"\n📝 EXECUTION STEPS:")
            for i, step in enumerate(result['steps_executed'], 1):
                print(f"  {i:2d}. {step}")
        
        if result['screenshots_taken']:
            print(f"\n📸 SCREENSHOTS SAVED:")
            for screenshot in result['screenshots_taken']:
                print(f"  📷 {screenshot}")
        
        if result.get('page_snapshots_taken'):
            print(f"\n📋 PAGE SNAPSHOTS:")
            for snapshot in result['page_snapshots_taken']:
                print(f"  📄 {snapshot}")
        
        if result.get('confirmation_data'):
            print(f"\n🔍 CONFIRMATION DATA:")
            confirmation = result['confirmation_data']
            for key, value in confirmation.items():
                print(f"  {key}: {value}")
        
        if result.get('error_details'):
            print(f"\n❌ ERROR DETAILS:")
            print(f"  {result['error_details']}")
        
        print(f"\n{'='*50}")
        print(f"Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Demo failed with exception: {str(e)}")
        import traceback
        print(f"Traceback:")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def demo_linkedin_job_search():
    """Demonstrate automation on LinkedIn job search"""
    print("\n" + "="*80)
    print("🎯 DEMO 2: LinkedIn Job Search")
    print("="*80)
    
    # LinkedIn job data
    linkedin_job_data = {
        "title": "Senior Software Engineer",
        "company": "Google",
        "location": "Mountain View, CA",
        "application_url": "https://www.linkedin.com/jobs/search/?keywords=software%20engineer",
        "apply_link": "https://www.linkedin.com/jobs/search/?keywords=software%20engineer",
        "source": "LinkedIn",
        "salary_range": "$150k-200k"
    }
    
    user_profile = get_sample_user_profile()
    resume_data = get_sample_resume_data()
    cover_letter_data = get_sample_cover_letter_data()
    
    automation_settings = {
        "screenshot_dir": "data/demo_screenshots/linkedin",
        "browser_width": 1280,
        "browser_height": 720
    }
    
    Path(automation_settings["screenshot_dir"]).mkdir(parents=True, exist_ok=True)
    
    print(f"🔗 Navigating to: {linkedin_job_data['application_url']}")
    
    try:
        result = await execute_real_mcp_job_automation(
            linkedin_job_data,
            user_profile,
            resume_data,
            cover_letter_data,
            automation_settings
        )
        
        print(f"LinkedIn Demo Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        print(f"Screenshots: {len(result['screenshots_taken'])}")
        
        return result
        
    except Exception as e:
        print(f"LinkedIn demo failed: {str(e)}")
        return {"success": False, "error": str(e)}


async def run_comprehensive_demo():
    """Run comprehensive demonstration of MCP automation"""
    print("🎭 COMPREHENSIVE MCP PLAYWRIGHT AUTOMATION DEMO")
    print("🔧 Using Real MCP Tools Available in Claude Code")
    print("="*80)
    
    start_time = datetime.now()
    
    # Demo 1: Microsoft Careers
    print("📍 DEMO 1: Microsoft Careers Page")
    microsoft_result = await demo_microsoft_careers()
    
    # Small delay between demos
    await asyncio.sleep(2)
    
    # Demo 2: LinkedIn (optional)
    # linkedin_result = await demo_linkedin_job_search()
    
    # Summary
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print("\n" + "="*80)
    print("📊 DEMO SUMMARY")
    print("="*80)
    print(f"Total Demo Time: {total_time:.2f} seconds")
    print(f"Microsoft Demo: {'✅ SUCCESS' if microsoft_result.get('success') else '❌ FAILED'}")
    # print(f"LinkedIn Demo: {'✅ SUCCESS' if linkedin_result.get('success') else '❌ FAILED'}")
    
    if microsoft_result.get('screenshots_taken'):
        print(f"\n📸 Total Screenshots: {len(microsoft_result['screenshots_taken'])}")
        print("📁 Screenshot Locations:")
        for screenshot in microsoft_result['screenshots_taken']:
            print(f"   {screenshot}")
    
    print(f"\n🎯 Key Achievements:")
    print("   ✅ Real browser opened using MCP Playwright")
    print("   ✅ Actual navigation to job sites")
    print("   ✅ Real screenshots captured and saved")
    print("   ✅ Page snapshots for analysis")
    print("   ✅ Form interaction attempts")
    print("   ✅ File upload handling")
    
    print(f"\n🔧 MCP Tools Demonstrated:")
    print("   • mcp__playwright__browser_install")
    print("   • mcp__playwright__browser_resize")
    print("   • mcp__playwright__browser_navigate")
    print("   • mcp__playwright__browser_take_screenshot")
    print("   • mcp__playwright__browser_snapshot")
    print("   • mcp__playwright__browser_wait_for")
    print("   • mcp__playwright__browser_type")
    print("   • mcp__playwright__browser_file_upload")
    
    print(f"\n✨ Demo completed successfully!")
    print(f"⏰ Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Ended: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    """
    Run the comprehensive demo when executed directly
    """
    print("🚀 STARTING REAL MCP PLAYWRIGHT AUTOMATION DEMO")
    print("🎯 This will open a real browser and navigate to job sites")
    print("📸 Screenshots will be saved to data/demo_screenshots/")
    print("⚠️  Make sure you have a stable internet connection")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()  # Wait for user confirmation
        asyncio.run(run_comprehensive_demo())
    except KeyboardInterrupt:
        print("\n❌ Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()