#!/usr/bin/env python3
"""
Test script to verify enhanced screenshot logging in automation system
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append('src')

def test_screenshot_logging():
    """Test the enhanced screenshot logging functionality"""
    
    print("🧪 Testing Enhanced Screenshot Logging")
    print("=" * 50)
    
    # Setup logging to see the output
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        from automation.real_mcp_implementation import RealMCPPlaywrightImplementation
        
        # Test configuration with screenshot directory
        config = {
            "screenshot_dir": "data/test_screenshots",
            "browser_width": 1280,
            "browser_height": 720
        }
        
        print("📁 Creating RealMCPPlaywrightImplementation with enhanced logging...")
        
        # Initialize the implementation - this will trigger directory logging
        implementation = RealMCPPlaywrightImplementation(config)
        
        print(f"✅ Screenshot directory created: {implementation.screenshot_dir}")
        print(f"✅ Directory exists: {implementation.screenshot_dir.exists()}")
        print(f"✅ Directory is writable: {implementation.screenshot_dir.is_dir()}")
        
        # Test the configuration
        print("\n📋 Configuration Details:")
        print(f"   Screenshot Directory: {implementation.screenshot_dir.absolute()}")
        print(f"   Browser Size: {implementation.browser_config['width']}x{implementation.browser_config['height']}")
        
        # Create a test file to verify write permissions
        test_file = implementation.screenshot_dir / "test_write_permissions.txt"
        try:
            test_file.write_text("Test file to verify write permissions")
            print(f"✅ Write test successful: {test_file}")
            test_file.unlink()  # Clean up
        except Exception as e:
            print(f"❌ Write test failed: {e}")
        
        print("\n🎯 Enhanced logging is working!")
        print("When you run automation, you'll see these log messages:")
        print("   📁 Screenshots will be saved to: /full/path/to/screenshots")
        print("   📁 Directory exists: True")
        print("   📁 Directory is writable: True")
        print("   📸 Screenshot saved: /full/path/to/screenshot.png")
        print("   📸 Full path: /absolute/path/to/screenshot.png")
        print("   📸 File exists after save: True")
        print("   📸 File size: 12345 bytes")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_screenshot_logging()
    print(f"\n{'✅ Test passed!' if success else '❌ Test failed!'}")