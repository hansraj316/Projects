import os
import yaml
import logging
from typing import Dict, List, Optional
from pathlib import Path

from agents.planner import Planner
from agents.executor import Executor
from agents.memory import Memory
from tools.web_search import WebSearch
from tools.file_manager import FileManager
from tools.api_connector import APIConnector

class AIAgentSystem:
    """
    Main class that orchestrates the AI agent system components.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._initialize_components()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from the specified path or use default."""
        default_path = Path(__file__).parent / "configs" / "settings.yaml"
        config_path = Path(config_path) if config_path else default_path
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}
    
    def _setup_logging(self) -> None:
        """Configure logging based on settings."""
        log_config = self.config.get('logging', {})
        logging.basicConfig(
            level=log_config.get('level', 'INFO'),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            filename=log_config.get('file')
        )
    
    def _initialize_components(self) -> None:
        """Initialize all system components."""
        # Initialize agents
        self.planner = Planner(self.config.get('agents', {}).get('planner'))
        self.executor = Executor(self.config.get('agents', {}).get('executor'))
        self.memory = Memory(self.config.get('agents', {}).get('memory'))
        
        # Initialize tools
        self.web_search = WebSearch(os.getenv('SEARCH_API_KEY'))
        self.file_manager = FileManager()
        self.api_connector = APIConnector(
            base_url=os.getenv('API_BASE_URL'),
            api_key=os.getenv('API_KEY')
        )
    
    def process_task(self, task: str) -> Dict:
        """
        Process a task through the agent system.
        
        Args:
            task: Task description or query
            
        Returns:
            Task processing results
        """
        try:
            # Create execution plan
            plan = self.planner.create_plan(task)
            if not self.planner.validate_plan(plan):
                raise ValueError("Invalid plan generated")
            
            # Execute plan
            results = self.executor.execute_plan(plan)
            
            # Store results in memory
            self.memory.add_to_memory({
                "task": task,
                "plan": plan,
                "results": results
            })
            
            return {
                "status": "success",
                "task": task,
                "results": results
            }
            
        except Exception as e:
            logging.error(f"Error processing task: {e}")
            return {
                "status": "error",
                "task": task,
                "error": str(e)
            }
    
    def get_task_history(self) -> List[Dict]:
        """Retrieve task execution history from memory."""
        return self.memory.short_term_memory

def main():
    # Initialize the AI agent system
    agent_system = AIAgentSystem()
    
    # Example usage
    task = "Search for information about AI agents and save the results"
    result = agent_system.process_task(task)
    
    if result["status"] == "success":
        print(f"Task completed successfully: {result['results']}")
    else:
        print(f"Error processing task: {result['error']}")

if __name__ == "__main__":
    main() 