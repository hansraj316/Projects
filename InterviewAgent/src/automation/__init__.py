"""
Automation package for InterviewAgent
Contains scheduling, MCP Playwright integration, and automation orchestration components
"""

from .scheduler import AutomationScheduler
from .playwright_mcp import PlaywrightMCPManager
from .mcp_playwright_integration import MCPPlaywrightAutomator, execute_mcp_playwright_automation
from .mcp_playwright_agent import MCPPlaywrightAgent, execute_mcp_playwright_job_automation
from .real_mcp_playwright_executor import RealMCPPlaywrightExecutor, execute_real_mcp_playwright_job_automation_with_tools
from .mcp_playwright_tools_caller import MCPPlaywrightToolsCaller, execute_mcp_tools_job_automation
from .mcp_playwright_executor import execute_real_mcp_playwright_automation_final
from .real_mcp_implementation import RealMCPPlaywrightImplementation, execute_real_mcp_job_automation

__all__ = [
    "AutomationScheduler", 
    "PlaywrightMCPManager", 
    "MCPPlaywrightAutomator", 
    "execute_mcp_playwright_automation",
    "MCPPlaywrightAgent",
    "execute_mcp_playwright_job_automation",
    "RealMCPPlaywrightExecutor",
    "execute_real_mcp_playwright_job_automation_with_tools",
    "MCPPlaywrightToolsCaller",
    "execute_mcp_tools_job_automation",
    "execute_real_mcp_playwright_automation_final",
    "RealMCPPlaywrightImplementation",
    "execute_real_mcp_job_automation"
]