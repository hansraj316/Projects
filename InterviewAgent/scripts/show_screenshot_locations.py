#!/usr/bin/env python3
"""
Screenshot Location Information for InterviewAgent
Shows where screenshots are saved and verifies directory structure
"""

import os
from pathlib import Path

def show_screenshot_locations():
    """Display all screenshot locations used by InterviewAgent"""
    
    print("📸 InterviewAgent Screenshot Locations")
    print("=" * 60)
    
    # Main project directory
    project_dir = Path(__file__).parent.absolute()
    print(f"🏠 Project Directory: {project_dir}")
    
    # Screenshot locations from the codebase
    screenshot_locations = [
        # Primary location (real_mcp_implementation.py)
        project_dir / "data" / "screenshots",
        
        # Demo location (demo_real_mcp_automation.py)  
        project_dir / "data" / "demo_screenshots",
        
        # LinkedIn demo location
        project_dir / "data" / "demo_screenshots" / "linkedin",
        
        # Test location (used in some tests)
        project_dir / "data" / "test_screenshots",
        
        # Legacy locations (from other implementations)
        Path("/tmp/screenshots"),
        Path("/tmp/interview-agent-screenshots"),
    ]
    
    print("\n📁 Screenshot Directory Locations:")
    print("-" * 40)
    
    for i, location in enumerate(screenshot_locations, 1):
        print(f"\n{i}. {location}")
        print(f"   Absolute path: {location.absolute()}")
        print(f"   Exists: {'✅ Yes' if location.exists() else '❌ No'}")
        print(f"   Writable: {'✅ Yes' if location.exists() and os.access(location, os.W_OK) else '❌ No'}")
        
        if location.exists():
            try:
                screenshots = list(location.glob("*.png")) + list(location.glob("*.jpg"))
                print(f"   Screenshots found: {len(screenshots)}")
                if screenshots:
                    print("   Recent screenshots:")
                    for screenshot in sorted(screenshots, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                        size_kb = screenshot.stat().st_size / 1024
                        print(f"     📷 {screenshot.name} ({size_kb:.1f} KB)")
            except Exception as e:
                print(f"   Error reading directory: {e}")
    
    print("\n🔧 Creating Missing Directories:")
    print("-" * 40)
    
    for location in screenshot_locations[:4]:  # Only create project directories, not /tmp
        try:
            location.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created/verified: {location}")
        except Exception as e:
            print(f"❌ Failed to create {location}: {e}")
    
    print("\n📋 Configuration Summary:")
    print("-" * 40)
    print("Primary automation screenshots: data/screenshots/")
    print("Demo screenshots: data/demo_screenshots/")
    print("Test screenshots: data/test_screenshots/")
    print("\nTo view screenshots after automation:")
    print(f"ls -la {project_dir}/data/screenshots/")
    print(f"open {project_dir}/data/screenshots/  # macOS")
    
    print("\n🎯 During automation, look for log messages like:")
    print("   📁 Screenshots will be saved to: /path/to/data/screenshots")
    print("   📸 Screenshot saved: /path/to/screenshot.png")
    print("   📸 File exists after save: True")
    print("   📸 File size: 12345 bytes")

if __name__ == "__main__":
    show_screenshot_locations()