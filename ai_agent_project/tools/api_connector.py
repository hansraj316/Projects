from typing import Dict, List, Optional
import requests
import json
from urllib.parse import urljoin

class APIConnector:
    """
    Tool for managing connections and interactions with external APIs.
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def request(self, 
                method: str, 
                endpoint: str, 
                data: Optional[Dict] = None, 
                params: Optional[Dict] = None,
                headers: Optional[Dict] = None) -> Dict:
        """
        Make an HTTP request to an API endpoint.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response data and metadata
        """
        try:
            url = urljoin(self.base_url, endpoint) if self.base_url else endpoint
            
            response = self.session.request(
                method=method.upper(),
                url=url,
                json=data if data else None,
                params=params if params else None,
                headers=headers if headers else None
            )
            
            response.raise_for_status()
            
            return {
                "status": "success",
                "status_code": response.status_code,
                "data": response.json() if response.content else None,
                "headers": dict(response.headers)
            }
        except requests.RequestException as e:
            return {
                "status": "error",
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Convenience method for GET requests."""
        return self.request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Dict) -> Dict:
        """Convenience method for POST requests."""
        return self.request("POST", endpoint, data=data)
    
    def put(self, endpoint: str, data: Dict) -> Dict:
        """Convenience method for PUT requests."""
        return self.request("PUT", endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict:
        """Convenience method for DELETE requests."""
        return self.request("DELETE", endpoint) 