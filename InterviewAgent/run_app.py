#!/usr/bin/env python3
"""
InterviewAgent Startup Script
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import plotly
        import pandas
        import supabase
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def run_tests():
    """Run basic tests"""
    print("🧪 Running basic tests...")
    result = subprocess.run([sys.executable, "test_app.py"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed:")
        print(result.stdout)
        print(result.stderr)
        return False

def start_streamlit():
    """Start the Streamlit application"""
    print("🚀 Starting InterviewAgent Streamlit App...")
    print("📱 App will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main startup function"""
    print("🤖 InterviewAgent - AI-Powered Job Application System")
    print("=" * 55)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Creating from example...")
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ .env file created. Please update with your actual configuration.")
        else:
            print("❌ .env.example not found. Please create a .env file manually.")
            return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Run tests
    if not run_tests():
        print("⚠️  Tests failed, but continuing anyway (mock mode)")
    
    # Start the application
    start_streamlit()

if __name__ == "__main__":
    main()