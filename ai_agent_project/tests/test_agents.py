import unittest
from unittest.mock import Mock, patch
from ..agents.planner import Planner
from ..agents.executor import Executor
from ..agents.memory import Memory

class TestPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = Planner()
    
    def test_create_plan(self):
        task = "Search for information about AI agents"
        plan = self.planner.create_plan(task)
        self.assertIsInstance(plan, list)
    
    def test_validate_plan(self):
        plan = [
            {"action": "web_search", "params": {"query": "AI agents"}},
            {"action": "save_results", "params": {"format": "json"}}
        ]
        is_valid = self.planner.validate_plan(plan)
        self.assertTrue(is_valid)
    
    def test_adjust_plan(self):
        plan = [{"action": "web_search", "params": {"query": "AI agents"}}]
        feedback = {"status": "error", "message": "Rate limit exceeded"}
        adjusted_plan = self.planner.adjust_plan(plan, feedback)
        self.assertIsInstance(adjusted_plan, list)

class TestExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = Executor()
    
    @patch('requests.get')
    def test_execute_step(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": "test"}
        
        step = {
            "action": "web_search",
            "params": {"query": "test"}
        }
        result = self.executor.execute_step(step)
        self.assertEqual(result["status"], "pending")
    
    def test_execute_plan(self):
        plan = [
            {"action": "web_search", "params": {"query": "test"}},
            {"action": "save_results", "params": {"data": "test"}}
        ]
        results = self.executor.execute_plan(plan)
        self.assertIsInstance(results, list)
    
    def test_handle_error(self):
        error = Exception("Test error")
        step = {"action": "web_search", "params": {"query": "test"}}
        result = self.executor.handle_error(error, step)
        self.assertEqual(result["status"], "error")

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
    
    def test_add_to_memory(self):
        entry = {"key": "test", "value": "data"}
        self.memory.add_to_memory(entry)
        self.assertGreater(len(self.memory.short_term_memory), 0)
    
    def test_get_relevant_context(self):
        self.memory.add_to_memory({"key": "test", "value": "data"})
        context = self.memory.get_relevant_context({"key": "test"})
        self.assertIsInstance(context, dict)
    
    def test_cleanup_short_term_memory(self):
        # Add more entries than the default max size
        for i in range(1100):
            self.memory.add_to_memory({"key": f"test_{i}"})
        self.assertLessEqual(len(self.memory.short_term_memory), 1000)

if __name__ == '__main__':
    unittest.main() 