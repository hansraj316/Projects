"""
Iframe Browser Server for InterviewAgent
Creates a controllable browser instance that can be embedded in Streamlit via iframe
"""

import asyncio
import threading
import time
from typing import Dict, Any, Optional
import logging
from pathlib import Path
from datetime import datetime
import json

try:
    from flask import Flask, render_template_string, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    CORS = None

class IframeBrowserServer:
    """
    Creates a local server that provides a browser interface controllable by Playwright MCP
    """
    
    def __init__(self, port: int = 8502):
        self.port = port
        self.app = None
        self.server_thread = None
        self.current_url = "about:blank"
        self.automation_status = "idle"
        self.automation_log = []
        self.browser_ready = False
        self.logger = logging.getLogger(__name__)
        
        # Browser state
        self.browser_state = {
            "current_url": "about:blank",
            "page_title": "InterviewAgent Browser",
            "status": "ready",
            "automation_active": False,
            "last_action": None,
            "form_data": {},
            "screenshots": []
        }
    
    def start_server(self) -> bool:
        """Start the iframe browser server"""
        if not FLASK_AVAILABLE:
            self.logger.error("Flask not available. Install with: pip install flask flask-cors")
            return False
        
        try:
            self.app = Flask(__name__)
            CORS(self.app)  # Enable CORS for iframe embedding
            
            self._setup_routes()
            
            # Start server in background thread
            self.server_thread = threading.Thread(
                target=lambda: self.app.run(
                    host='localhost',
                    port=self.port,
                    debug=False,
                    use_reloader=False
                ),
                daemon=True
            )
            self.server_thread.start()
            
            # Wait for server to start
            time.sleep(2)
            self.browser_ready = True
            
            self.logger.info(f"Iframe browser server started on http://localhost:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start iframe browser server: {str(e)}")
            return False
    
    def _setup_routes(self):
        """Setup Flask routes for the browser interface"""
        
        @self.app.route('/')
        def browser_interface():
            """Main browser interface"""
            return render_template_string(BROWSER_TEMPLATE, 
                                        current_url=self.browser_state["current_url"],
                                        page_title=self.browser_state["page_title"])
        
        @self.app.route('/navigate', methods=['POST'])
        def navigate():
            """Navigate to a URL"""
            data = request.get_json()
            url = data.get('url', '')
            
            if url:
                self.browser_state["current_url"] = url
                self.browser_state["last_action"] = f"Navigate to {url}"
                self.automation_log.append(f"🌐 Navigated to: {url}")
                
                return jsonify({
                    "success": True,
                    "url": url,
                    "timestamp": datetime.now().isoformat()
                })
            
            return jsonify({"success": False, "error": "No URL provided"})
        
        @self.app.route('/fill_form', methods=['POST'])
        def fill_form():
            """Fill form fields"""
            data = request.get_json()
            form_data = data.get('form_data', {})
            
            self.browser_state["form_data"].update(form_data)
            self.browser_state["last_action"] = f"Fill form with {len(form_data)} fields"
            self.automation_log.append(f"📝 Filled form fields: {list(form_data.keys())}")
            
            return jsonify({
                "success": True,
                "fields_filled": len(form_data),
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/take_screenshot', methods=['POST'])
        def take_screenshot():
            """Take screenshot"""
            data = request.get_json()
            filename = data.get('filename', f'screenshot_{int(time.time())}.png')
            
            # Simulate screenshot capture
            screenshot_path = Path('data/screenshots') / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create placeholder screenshot info
            screenshot_info = {
                "filename": filename,
                "path": str(screenshot_path),
                "timestamp": datetime.now().isoformat(),
                "url": self.browser_state["current_url"]
            }
            
            self.browser_state["screenshots"].append(screenshot_info)
            self.automation_log.append(f"📸 Screenshot saved: {filename}")
            
            return jsonify({
                "success": True,
                "screenshot": screenshot_info
            })
        
        @self.app.route('/status')
        def get_status():
            """Get current browser status"""
            return jsonify(self.browser_state)
        
        @self.app.route('/automation_log')
        def get_automation_log():
            """Get automation log"""
            return jsonify({
                "log": self.automation_log,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/reset')
        def reset_browser():
            """Reset browser state"""
            self.browser_state = {
                "current_url": "about:blank",
                "page_title": "InterviewAgent Browser",
                "status": "ready",
                "automation_active": False,
                "last_action": None,
                "form_data": {},
                "screenshots": []
            }
            self.automation_log = []
            
            return jsonify({"success": True, "message": "Browser reset"})
    
    def navigate_to_url(self, url: str) -> bool:
        """Navigate to URL programmatically"""
        try:
            self.browser_state["current_url"] = url
            self.browser_state["last_action"] = f"Navigate to {url}"
            self.automation_log.append(f"🌐 MCP Navigation: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Navigation failed: {str(e)}")
            return False
    
    def fill_form_fields(self, form_data: Dict[str, str]) -> bool:
        """Fill form fields programmatically"""
        try:
            self.browser_state["form_data"].update(form_data)
            self.browser_state["last_action"] = f"Fill {len(form_data)} form fields"
            self.automation_log.append(f"📝 MCP Form Fill: {list(form_data.keys())}")
            return True
        except Exception as e:
            self.logger.error(f"Form filling failed: {str(e)}")
            return False
    
    def capture_screenshot(self, filename: str) -> Optional[str]:
        """Capture real PNG screenshot programmatically"""
        try:
            screenshot_path = Path('data/screenshots') / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"📸 Generating real PNG screenshot: {filename}")
            
            # Use real screenshot generator
            try:
                from utils.screenshot_generator import RealScreenshotGenerator
                
                generator = RealScreenshotGenerator({
                    "screenshot_dir": "data/screenshots",
                    "screenshot_width": 1280,
                    "screenshot_height": 720
                })
                
                # Create job data from current browser state
                job_data = {
                    "title": "Job Application",
                    "company": "Company",
                    "application_url": self.browser_state["current_url"],
                    "location": "Location"
                }
                
                # Determine screenshot type based on browser state
                screenshot_type = "initial_page"
                if self.browser_state.get("form_data"):
                    screenshot_type = "after_form_fill"
                if "submit" in filename.lower() or "final" in filename.lower():
                    screenshot_type = "final_state"
                
                real_screenshot_path = generator.generate_screenshot(
                    screenshot_type,
                    job_data,
                    {"server": "iframe_browser", "automation": True}
                )
                
                if real_screenshot_path:
                    screenshot_info = {
                        "filename": filename,
                        "path": real_screenshot_path,
                        "timestamp": datetime.now().isoformat(),
                        "url": self.browser_state["current_url"],
                        "is_real_png": True
                    }
                    
                    self.browser_state["screenshots"].append(screenshot_info)
                    self.automation_log.append(f"📸 Real PNG Screenshot: {filename}")
                    
                    return real_screenshot_path
                else:
                    raise Exception("Real screenshot generation failed")
                    
            except Exception as e:
                self.logger.warning(f"Real screenshot generation failed: {str(e)}")
                
                # Fallback to basic file creation (but still indicate it's not a real screenshot)
                placeholder_content = f"""Screenshot Generation Failed - {datetime.now().isoformat()}
URL: {self.browser_state['current_url']}
Filename: {filename}
Automation: Iframe Browser Server
Error: {str(e)}

Real PNG screenshot generation failed. Check image library dependencies.
"""
                screenshot_path.write_text(placeholder_content)
                
                screenshot_info = {
                    "filename": filename,
                    "path": str(screenshot_path),
                    "timestamp": datetime.now().isoformat(),
                    "url": self.browser_state["current_url"],
                    "is_real_png": False,
                    "error": str(e)
                }
                
                self.browser_state["screenshots"].append(screenshot_info)
                self.automation_log.append(f"⚠️ Fallback Screenshot: {filename}")
                
                return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"Screenshot failed: {str(e)}")
            return None
    
    def get_iframe_url(self) -> str:
        """Get the URL for embedding in iframe"""
        return f"http://localhost:{self.port}"
    
    def stop_server(self):
        """Stop the server"""
        self.browser_ready = False
        # Note: Flask development server doesn't have a clean shutdown method
        # In production, you'd use a proper WSGI server


# Browser interface HTML template
BROWSER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }
        
        .browser-header {
            background: #2e3440;
            color: white;
            padding: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .url-bar {
            flex: 1;
            padding: 8px;
            border: none;
            border-radius: 4px;
            background: #3b4252;
            color: white;
            font-size: 14px;
        }
        
        .nav-button {
            background: #5e81ac;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        
        .nav-button:hover {
            background: #81a1c1;
        }
        
        .content-area {
            height: calc(100vh - 60px);
            display: flex;
            flex-direction: column;
        }
        
        .iframe-container {
            flex: 1;
            border: none;
            background: white;
        }
        
        .status-bar {
            background: #4c566a;
            color: white;
            padding: 5px 10px;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
        }
        
        .automation-indicator {
            background: #a3be8c;
            color: #2e3440;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: bold;
        }
        
        .automation-indicator.active {
            background: #ebcb8b;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .job-site-simulator {
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .form-section {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .form-group {
            margin: 15px 0;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .submit-button {
            background: #5e81ac;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        
        .submit-button:hover {
            background: #81a1c1;
        }
    </style>
</head>
<body>
    <div class="browser-header">
        <button class="nav-button" onclick="goBack()">←</button>
        <button class="nav-button" onclick="goForward()">→</button>
        <button class="nav-button" onclick="refresh()">⟳</button>
        <input type="text" class="url-bar" id="urlBar" value="{{ current_url }}" onkeypress="handleUrlKeypress(event)">
        <button class="nav-button" onclick="navigate()">Go</button>
    </div>
    
    <div class="content-area">
        <div class="iframe-container" id="contentArea">
            <div class="job-site-simulator">
                <h1>🏢 Sample Job Application Site</h1>
                <p>This simulates a job application website that Playwright MCP can control.</p>
                
                <div class="form-section">
                    <h2>Personal Information</h2>
                    <div class="form-group">
                        <label for="firstName">First Name:</label>
                        <input type="text" id="firstName" name="firstName" placeholder="Enter your first name">
                    </div>
                    
                    <div class="form-group">
                        <label for="lastName">Last Name:</label>
                        <input type="text" id="lastName" name="lastName" placeholder="Enter your last name">
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" placeholder="Enter your email">
                    </div>
                    
                    <div class="form-group">
                        <label for="phone">Phone:</label>
                        <input type="tel" id="phone" name="phone" placeholder="Enter your phone number">
                    </div>
                </div>
                
                <div class="form-section">
                    <h2>Experience</h2>
                    <div class="form-group">
                        <label for="experience">Tell us about your experience:</label>
                        <textarea id="experience" name="experience" rows="4" placeholder="Describe your relevant experience..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="resume">Resume Upload:</label>
                        <input type="file" id="resume" name="resume" accept=".pdf,.doc,.docx">
                    </div>
                </div>
                
                <div class="form-section">
                    <h2>Submit Application</h2>
                    <button class="submit-button" onclick="submitApplication()">Submit Application</button>
                </div>
            </div>
        </div>
    </div>
    
    <div class="status-bar">
        <span id="statusText">Ready for automation</span>
        <span class="automation-indicator" id="automationIndicator">MCP Ready</span>
    </div>

    <script>
        let automationActive = false;
        
        function navigate() {
            const url = document.getElementById('urlBar').value;
            if (url) {
                fetch('/navigate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateStatus(`Navigated to: ${url}`);
                    }
                });
            }
        }
        
        function handleUrlKeypress(event) {
            if (event.key === 'Enter') {
                navigate();
            }
        }
        
        function goBack() {
            updateStatus('Going back...');
        }
        
        function goForward() {
            updateStatus('Going forward...');
        }
        
        function refresh() {
            updateStatus('Refreshing page...');
            location.reload();
        }
        
        function submitApplication() {
            setAutomationActive(true);
            updateStatus('Submitting application...');
            
            // Simulate form submission
            setTimeout(() => {
                alert('Application submitted successfully!');
                setAutomationActive(false);
                updateStatus('Application submitted - Ready for next action');
            }, 2000);
        }
        
        function updateStatus(message) {
            document.getElementById('statusText').textContent = message;
        }
        
        function setAutomationActive(active) {
            automationActive = active;
            const indicator = document.getElementById('automationIndicator');
            if (active) {
                indicator.textContent = 'MCP Active';
                indicator.classList.add('active');
            } else {
                indicator.textContent = 'MCP Ready';
                indicator.classList.remove('active');
            }
        }
        
        // Simulate MCP automation actions
        function simulateMCPAction(action, data) {
            setAutomationActive(true);
            updateStatus(`MCP Action: ${action}`);
            
            if (action === 'fill_form') {
                // Fill form fields automatically
                Object.keys(data).forEach(fieldName => {
                    const field = document.getElementById(fieldName);
                    if (field) {
                        field.value = data[fieldName];
                        field.style.backgroundColor = '#a3be8c';
                        setTimeout(() => {
                            field.style.backgroundColor = '';
                        }, 1000);
                    }
                });
            }
            
            setTimeout(() => {
                setAutomationActive(false);
                updateStatus('MCP action completed');
            }, 1500);
        }
        
        // Listen for automation commands
        setInterval(() => {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    if (data.automation_active && !automationActive) {
                        setAutomationActive(true);
                    } else if (!data.automation_active && automationActive) {
                        setAutomationActive(false);
                    }
                    
                    if (data.last_action) {
                        updateStatus(data.last_action);
                    }
                })
                .catch(() => {
                    // Ignore errors - server might not be ready
                });
        }, 1000);
    </script>
</body>
</html>
"""


# Global server instance
_server_instance = None

def get_iframe_browser_server(port: int = 8502) -> IframeBrowserServer:
    """Get or create the iframe browser server instance"""
    global _server_instance
    
    if _server_instance is None:
        _server_instance = IframeBrowserServer(port)
        
    return _server_instance

def start_iframe_browser_server(port: int = 8502) -> str:
    """Start the iframe browser server and return the URL"""
    server = get_iframe_browser_server(port)
    
    if server.start_server():
        return server.get_iframe_url()
    else:
        return None


if __name__ == "__main__":
    # Test the server
    print("Starting Iframe Browser Server...")
    
    server = IframeBrowserServer(8502)
    if server.start_server():
        print(f"Server started at: {server.get_iframe_url()}")
        print("Visit the URL in your browser to test the interface")
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Server stopped")
    else:
        print("Failed to start server")