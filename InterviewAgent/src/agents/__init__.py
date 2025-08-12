"""
AI Agents package for InterviewAgent
"""

try:
    from agents.base_agent import BaseAgent, AgentTask, AgentContext
    from agents.resume_optimizer import ResumeOptimizerAgent
    from agents.cover_letter_generator import CoverLetterAgent
    from agents.job_discovery import JobDiscoveryAgent
    
    # Try to import enhanced orchestrator and agent_manager if they exist
    try:
        from agents.enhanced_orchestrator import EnhancedOrchestratorAgent
        from agents.agent_manager import AgentManager
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