import unittest
from unittest.mock import Mock, patch
import tempfile
import os
from pathlib import Path
from ..tools.web_search import WebSearch
from ..tools.file_manager import FileManager
from ..tools.api_connector import APIConnector

class TestWebSearch(unittest.TestCase):
    def setUp(self):
        self.web_search = WebSearch(api_key="test_key")
    
    @patch('requests.get')
    def test_search(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "results": [{"title": "Test", "url": "http://test.com"}]
        }
        
        results = self.web_search.search("AI agents")
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
    
    @patch('requests.get')
    def test_extract_content(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html>Test content</html>"
        
        result = self.web_search.extract_content("http://test.com")
        self.assertEqual(result["status"], "success")
        self.assertIsNotNone(result["content"])

class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = FileManager(base_path=self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_write_and_read_file(self):
        content = {"test": "data"}
        result = self.file_manager.write_file(
            "test.json",
            content,
            file_type="json"
        )
        self.assertEqual(result["status"], "success")
        
        read_result = self.file_manager.read_file(
            "test.json",
            file_type="json"
        )
        self.assertEqual(read_result["status"], "success")
        self.assertEqual(read_result["content"], content)
    
    def test_list_directory(self):
        # Create some test files
        Path(self.temp_dir, "test1.txt").touch()
        Path(self.temp_dir, "test2.txt").touch()
        
        result = self.file_manager.list_directory()
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["contents"]), 2)

class TestAPIConnector(unittest.TestCase):
    def setUp(self):
        self.api_connector = APIConnector(
            base_url="http://api.test.com",
            api_key="test_key"
        )
    
    @patch('requests.Session.request')
    def test_get_request(self, mock_request):
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {"data": "test"}
        
        result = self.api_connector.get("/endpoint")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["status_code"], 200)
    
    @patch('requests.Session.request')
    def test_post_request(self, mock_request):
        mock_request.return_value.status_code = 201
        mock_request.return_value.json.return_value = {"id": 1}
        
        result = self.api_connector.post("/endpoint", {"data": "test"})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["status_code"], 201)
    
    @patch('requests.Session.request')
    def test_error_handling(self, mock_request):
        mock_request.side_effect = Exception("Test error")
        
        result = self.api_connector.get("/endpoint")
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main() 