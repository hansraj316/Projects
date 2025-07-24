"""
Automation package for InterviewAgent
Contains essential automation components: scheduling and MCP implementation
"""

from .scheduler import AutomationScheduler
from .real_mcp_implementation import RealMCPPlaywrightImplementation, execute_real_mcp_job_automation

__all__ = [
    "AutomationScheduler",
    "RealMCPPlaywrightImplementation", 
    "execute_real_mcp_job_automation"
]