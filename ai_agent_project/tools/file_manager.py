from typing import Dict, List, Optional, BinaryIO
import os
import json
import yaml
from pathlib import Path

class FileManager:
    """
    Tool for managing file operations, including reading, writing,
    and handling different file formats.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
    
    def read_file(self, file_path: str, file_type: str = "text") -> Dict:
        """
        Read file contents based on file type.
        
        Args:
            file_path: Path to the file
            file_type: Type of file (text, json, yaml, binary)
            
        Returns:
            File contents and metadata
        """
        try:
            full_path = self.base_path / file_path
            
            if file_type == "json":
                with open(full_path, 'r') as f:
                    content = json.load(f)
            elif file_type == "yaml":
                with open(full_path, 'r') as f:
                    content = yaml.safe_load(f)
            elif file_type == "binary":
                with open(full_path, 'rb') as f:
                    content = f.read()
            else:  # text
                with open(full_path, 'r') as f:
                    content = f.read()
                    
            return {
                "status": "success",
                "content": content,
                "path": str(full_path)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": str(full_path)
            }
    
    def write_file(self, file_path: str, content: any, file_type: str = "text") -> Dict:
        """
        Write content to a file.
        
        Args:
            file_path: Path to write the file to
            content: Content to write
            file_type: Type of file (text, json, yaml, binary)
            
        Returns:
            Operation status and metadata
        """
        try:
            full_path = self.base_path / file_path
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            if file_type == "json":
                with open(full_path, 'w') as f:
                    json.dump(content, f, indent=2)
            elif file_type == "yaml":
                with open(full_path, 'w') as f:
                    yaml.safe_dump(content, f)
            elif file_type == "binary":
                with open(full_path, 'wb') as f:
                    f.write(content)
            else:  # text
                with open(full_path, 'w') as f:
                    f.write(content)
                    
            return {
                "status": "success",
                "path": str(full_path)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": str(full_path)
            }
    
    def list_directory(self, dir_path: Optional[str] = None) -> Dict:
        """
        List contents of a directory.
        
        Args:
            dir_path: Path to the directory
            
        Returns:
            Directory contents and metadata
        """
        try:
            full_path = self.base_path / (dir_path or "")
            contents = list(full_path.iterdir())
            
            return {
                "status": "success",
                "contents": [
                    {
                        "name": item.name,
                        "type": "file" if item.is_file() else "directory",
                        "size": item.stat().st_size if item.is_file() else None
                    }
                    for item in contents
                ],
                "path": str(full_path)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": str(full_path)
            } 