"""
Repository interfaces for data access layer

Defines contracts for data access operations following repository pattern.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Generic, TypeVar
from datetime import datetime

# Generic type for entity
T = TypeVar('T')

class IRepository(Generic[T], ABC):
    """Base repository interface"""
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """Get all entities with optional pagination"""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity"""
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, entity: T) -> Optional[T]:
        """Update existing entity"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """Check if entity exists"""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters"""
        pass

class IJobRepository(IRepository):
    """Job listing repository interface"""
    
    @abstractmethod
    async def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find jobs by search criteria"""
        pass
    
    @abstractmethod
    async def find_by_company(self, company_name: str) -> List[Dict[str, Any]]:
        """Find jobs by company name"""
        pass
    
    @abstractmethod
    async def find_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Find jobs by location"""
        pass
    
    @abstractmethod
    async def find_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Find jobs by keywords"""
        pass
    
    @abstractmethod
    async def find_recent(self, days: int = 7) -> List[Dict[str, Any]]:
        """Find jobs posted in the last N days"""
        pass
    
    @abstractmethod
    async def update_status(self, job_id: str, status: str) -> bool:
        """Update job status"""
        pass
    
    @abstractmethod
    async def mark_as_applied(self, job_id: str, application_date: datetime) -> bool:
        """Mark job as applied"""
        pass

class IApplicationRepository(IRepository):
    """Job application repository interface"""
    
    @abstractmethod
    async def find_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Find applications by user ID"""
        pass
    
    @abstractmethod
    async def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Find applications by status"""
        pass
    
    @abstractmethod
    async def find_by_job(self, job_id: str) -> List[Dict[str, Any]]:
        """Find applications for a specific job"""
        pass
    
    @abstractmethod
    async def get_application_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get application history for user"""
        pass
    
    @abstractmethod
    async def update_status(self, application_id: str, status: str, notes: Optional[str] = None) -> bool:
        """Update application status"""
        pass
    
    @abstractmethod
    async def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get application statistics for user"""
        pass

class IResumeRepository(IRepository):
    """Resume repository interface"""
    
    @abstractmethod
    async def find_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Find resumes by user ID"""
        pass
    
    @abstractmethod
    async def find_by_template(self, template_id: str) -> List[Dict[str, Any]]:
        """Find resumes by template ID"""
        pass
    
    @abstractmethod
    async def get_active_resume(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's active resume"""
        pass
    
    @abstractmethod
    async def set_active_resume(self, user_id: str, resume_id: str) -> bool:
        """Set resume as active for user"""
        pass
    
    @abstractmethod
    async def get_versions(self, resume_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a resume"""
        pass
    
    @abstractmethod
    async def create_version(self, resume_id: str, content: str, notes: Optional[str] = None) -> str:
        """Create new version of a resume"""
        pass

class IUserRepository(IRepository):
    """User repository interface"""
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        pass
    
    @abstractmethod
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        pass
    
    @abstractmethod
    async def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        pass
    
    @abstractmethod
    async def update_last_active(self, user_id: str) -> bool:
        """Update user's last active timestamp"""
        pass
    
    @abstractmethod
    async def get_activity_log(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user activity log"""
        pass

class INotificationRepository(IRepository):
    """Notification repository interface"""
    
    @abstractmethod
    async def find_by_user(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Find notifications by user"""
        pass
    
    @abstractmethod
    async def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        pass
    
    @abstractmethod
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for user"""
        pass
    
    @abstractmethod
    async def delete_old_notifications(self, days: int = 30) -> int:
        """Delete notifications older than N days"""
        pass
    
    @abstractmethod
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        pass

class ICredentialRepository(IRepository):
    """Credential repository interface for secure storage"""
    
    @abstractmethod
    async def store_encrypted_credential(self, user_id: str, service: str, encrypted_data: str) -> str:
        """Store encrypted credential"""
        pass
    
    @abstractmethod
    async def get_encrypted_credential(self, user_id: str, service: str) -> Optional[str]:
        """Get encrypted credential"""
        pass
    
    @abstractmethod
    async def delete_credential(self, user_id: str, service: str) -> bool:
        """Delete credential"""
        pass
    
    @abstractmethod
    async def list_services(self, user_id: str) -> List[str]:
        """List services with stored credentials"""
        pass
    
    @abstractmethod
    async def rotate_credentials(self, user_id: str, service: str, new_encrypted_data: str) -> bool:
        """Rotate credentials for a service"""
        pass

class IAnalyticsRepository(IRepository):
    """Analytics repository interface"""
    
    @abstractmethod
    async def record_event(self, user_id: str, event_type: str, data: Dict[str, Any]) -> str:
        """Record analytics event"""
        pass
    
    @abstractmethod
    async def get_user_metrics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get user metrics for date range"""
        pass
    
    @abstractmethod
    async def get_system_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get system-wide metrics"""
        pass
    
    @abstractmethod
    async def get_popular_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular job postings"""
        pass
    
    @abstractmethod
    async def get_success_rates(self, user_id: Optional[str] = None) -> Dict[str, float]:
        """Get application success rates"""
        pass