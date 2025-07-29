"""
AI Agents package for InterviewAgent
"""

try:
    from .base_agent import BaseAgent, AgentTask, AgentContext
    from .resume_optimizer import ResumeOptimizerAgent
    from .cover_letter_generator import CoverLetterAgent
    from .job_discovery import JobDiscoveryAgent
    
    # Try to import enhanced orchestrator and agent_manager if they exist
    try:
        from .enhanced_orchestrator import EnhancedOrchestratorAgent
        from .agent_manager import AgentManager
        orchestrator_available = True
    except ImportError:
        EnhancedOrchestratorAgent = None
        AgentManager = None
        orchestrator_available = False
    
    __all__ = [
        'BaseAgent', 
        'AgentTask', 
        'AgentContext',
        'ResumeOptimizerAgent', 
        'CoverLetterAgent',
        'JobDiscoveryAgent'
    ]
    
    if orchestrator_available:
        __all__.extend(['EnhancedOrchestratorAgent', 'AgentManager'])
        
except ImportError as e:
    print(f"Warning: Could not import some agent modules: {e}")
    # Provide minimal imports for basic functionality
    BaseAgent = None
    AgentTask = None
    AgentContext = None
    ResumeOptimizerAgent = None
    CoverLetterAgent = None
    JobDiscoveryAgent = None
    EnhancedOrchestratorAgent = None
    AgentManager = None