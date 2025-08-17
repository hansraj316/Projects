"""
Supabase implementations of repository interfaces

Provides concrete implementations of repositories using Supabase as the data store.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging

from .interfaces import (
    IJobRepository, IApplicationRepository, IResumeRepository, 
    IUserRepository, INotificationRepository, ICredentialRepository,
    IAnalyticsRepository
)
from core.protocols import IDatabaseConnection, ILogger
from core.exceptions import DatabaseError, ValidationError

class BaseSupabaseRepository:
    """Base class for Supabase repositories"""
    
    def __init__(self, db_connection: IDatabaseConnection, logger: ILogger, table_name: str):
        self._db = db_connection
        self._logger = logger
        self._table_name = table_name
    
    async def _execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute query with error handling"""
        try:
            return await self._db.execute_query(query, params)
        except Exception as e:
            self._logger.error(f"Database query failed for table {self._table_name}", extra={
                'query': query,
                'params': params,
                'error': str(e)
            })
            raise DatabaseError(f"Query failed: {str(e)}") from e
    
    async def _execute_mutation(self, mutation: str, params: Optional[Dict] = None) -> Any:
        """Execute mutation with error handling"""
        try:
            return await self._db.execute_mutation(mutation, params)
        except Exception as e:
            self._logger.error(f"Database mutation failed for table {self._table_name}", extra={
                'mutation': mutation,
                'params': params,
                'error': str(e)
            })
            raise DatabaseError(f"Mutation failed: {str(e)}") from e
    
    def _validate_id(self, entity_id: str) -> None:
        """Validate entity ID"""
        if not entity_id or not isinstance(entity_id, str):
            raise ValidationError("entity_id", entity_id, "Entity ID must be a non-empty string")

class SupabaseJobRepository(BaseSupabaseRepository, IJobRepository):
    """Supabase implementation of job repository"""
    
    def __init__(self, db_connection: IDatabaseConnection, logger: ILogger):
        super().__init__(db_connection, logger, "job_listings")
    
    async def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        self._validate_id(entity_id)
        
        query = f"""
        SELECT * FROM {self._table_name}
        WHERE id = %(job_id)s
        """
        
        result = await self._execute_query(query, {"job_id": entity_id})
        return result.data[0] if result.data else None
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all jobs with pagination"""
        query = f"SELECT * FROM {self._table_name} ORDER BY created_at DESC"
        params = {}
        
        if limit:
            query += " LIMIT %(limit)s"
            params["limit"] = limit
        
        if offset:
            query += " OFFSET %(offset)s"
            params["offset"] = offset
        
        result = await self._execute_query(query, params)
        return result.data or []
    
    async def create(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Create new job listing"""
        # Validate required fields
        required_fields = ["title", "company", "location", "description"]
        for field in required_fields:
            if field not in entity:
                raise ValidationError(field, None, f"Required field {field} is missing")
        
        # Add timestamps
        now = datetime.utcnow()
        entity["created_at"] = now
        entity["updated_at"] = now
        
        mutation = f"""
        INSERT INTO {self._table_name} 
        (title, company, location, description, url, salary_range, requirements, 
         benefits, job_type, experience_level, remote_option, status, created_at, updated_at)
        VALUES 
        (%(title)s, %(company)s, %(location)s, %(description)s, %(url)s, %(salary_range)s,
         %(requirements)s, %(benefits)s, %(job_type)s, %(experience_level)s, 
         %(remote_option)s, %(status)s, %(created_at)s, %(updated_at)s)
        RETURNING *
        """
        
        result = await self._execute_mutation(mutation, entity)
        return result.data[0] if result.data else entity
    
    async def update(self, entity_id: str, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing job"""
        self._validate_id(entity_id)
        
        entity["updated_at"] = datetime.utcnow()
        entity["id"] = entity_id
        
        mutation = f"""
        UPDATE {self._table_name}
        SET title = %(title)s, company = %(company)s, location = %(location)s,
            description = %(description)s, url = %(url)s, salary_range = %(salary_range)s,
            requirements = %(requirements)s, benefits = %(benefits)s, 
            job_type = %(job_type)s, experience_level = %(experience_level)s,
            remote_option = %(remote_option)s, status = %(status)s, updated_at = %(updated_at)s
        WHERE id = %(id)s
        RETURNING *
        """
        
        result = await self._execute_mutation(mutation, entity)
        return result.data[0] if result.data else None
    
    async def delete(self, entity_id: str) -> bool:
        """Delete job by ID"""
        self._validate_id(entity_id)
        
        mutation = f"DELETE FROM {self._table_name} WHERE id = %(job_id)s"
        result = await self._execute_mutation(mutation, {"job_id": entity_id})
        return bool(result.data)
    
    async def exists(self, entity_id: str) -> bool:
        """Check if job exists"""
        self._validate_id(entity_id)
        
        query = f"SELECT 1 FROM {self._table_name} WHERE id = %(job_id)s"
        result = await self._execute_query(query, {"job_id": entity_id})
        return bool(result.data)
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count jobs with optional filters"""
        query = f"SELECT COUNT(*) as count FROM {self._table_name}"
        params = {}
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = %({key})s")
                params[key] = value
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        result = await self._execute_query(query, params)
        return result.data[0]["count"] if result.data else 0
    
    async def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find jobs by search criteria"""
        query = f"SELECT * FROM {self._table_name} WHERE 1=1"
        params = {}
        
        if "keywords" in criteria:
            query += " AND (title ILIKE %(keywords)s OR description ILIKE %(keywords)s)"
            params["keywords"] = f"%{criteria['keywords']}%"
        
        if "location" in criteria:
            query += " AND location ILIKE %(location)s"
            params["location"] = f"%{criteria['location']}%"
        
        if "company" in criteria:
            query += " AND company ILIKE %(company)s"
            params["company"] = f"%{criteria['company']}%"
        
        if "remote_only" in criteria and criteria["remote_only"]:
            query += " AND remote_option = true"
        
        if "salary_min" in criteria:
            query += " AND salary_range->>'min' >= %(salary_min)s"
            params["salary_min"] = str(criteria["salary_min"])
        
        query += " ORDER BY created_at DESC"
        
        if "limit" in criteria:
            query += " LIMIT %(limit)s"
            params["limit"] = criteria["limit"]
        
        result = await self._execute_query(query, params)
        return result.data or []
    
    async def find_by_company(self, company_name: str) -> List[Dict[str, Any]]:
        """Find jobs by company name"""
        query = f"""
        SELECT * FROM {self._table_name}
        WHERE company ILIKE %(company)s
        ORDER BY created_at DESC
        """
        
        result = await self._execute_query(query, {"company": f"%{company_name}%"})
        return result.data or []
    
    async def find_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Find jobs by location"""
        query = f"""
        SELECT * FROM {self._table_name}
        WHERE location ILIKE %(location)s
        ORDER BY created_at DESC
        """
        
        result = await self._execute_query(query, {"location": f"%{location}%"})
        return result.data or []
    
    async def find_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Find jobs by keywords"""
        if not keywords:
            return []
        
        # Build dynamic query for multiple keywords
        keyword_conditions = []
        params = {}
        
        for i, keyword in enumerate(keywords):
            param_name = f"keyword_{i}"
            keyword_conditions.append(f"(title ILIKE %({param_name})s OR description ILIKE %({param_name})s)")
            params[param_name] = f"%{keyword}%"
        
        query = f"""
        SELECT * FROM {self._table_name}
        WHERE {' OR '.join(keyword_conditions)}
        ORDER BY created_at DESC
        """
        
        result = await self._execute_query(query, params)
        return result.data or []
    
    async def find_recent(self, days: int = 7) -> List[Dict[str, Any]]:
        """Find jobs posted in the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = f"""
        SELECT * FROM {self._table_name}
        WHERE created_at >= %(cutoff_date)s
        ORDER BY created_at DESC
        """
        
        result = await self._execute_query(query, {"cutoff_date": cutoff_date})
        return result.data or []
    
    async def update_status(self, job_id: str, status: str) -> bool:
        """Update job status"""
        self._validate_id(job_id)
        
        mutation = f"""
        UPDATE {self._table_name}
        SET status = %(status)s, updated_at = %(updated_at)s
        WHERE id = %(job_id)s
        """
        
        params = {
            "job_id": job_id,
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        result = await self._execute_mutation(mutation, params)
        return bool(result.data)
    
    async def mark_as_applied(self, job_id: str, application_date: datetime) -> bool:
        """Mark job as applied"""
        self._validate_id(job_id)
        
        mutation = f"""
        UPDATE {self._table_name}
        SET status = 'applied', 
            applied_at = %(application_date)s,
            updated_at = %(updated_at)s
        WHERE id = %(job_id)s
        """
        
        params = {
            "job_id": job_id,
            "application_date": application_date,
            "updated_at": datetime.utcnow()
        }
        
        result = await self._execute_mutation(mutation, params)
        return bool(result.data)

class SupabaseApplicationRepository(BaseSupabaseRepository, IApplicationRepository):
    """Supabase implementation of application repository"""
    
    def __init__(self, db_connection: IDatabaseConnection, logger: ILogger):
        super().__init__(db_connection, logger, "applications")
    
    async def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get application by ID"""
        self._validate_id(entity_id)
        
        query = f"""
        SELECT a.*, j.title as job_title, j.company, j.location
        FROM {self._table_name} a
        LEFT JOIN job_listings j ON a.job_id = j.id
        WHERE a.id = %(application_id)s
        """
        
        result = await self._execute_query(query, {"application_id": entity_id})
        return result.data[0] if result.data else None
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all applications with pagination"""
        query = f"""
        SELECT a.*, j.title as job_title, j.company, j.location
        FROM {self._table_name} a
        LEFT JOIN job_listings j ON a.job_id = j.id
        ORDER BY a.created_at DESC
        """
        params = {}
        
        if limit:
            query += " LIMIT %(limit)s"
            params["limit"] = limit
        
        if offset:
            query += " OFFSET %(offset)s"
            params["offset"] = offset
        
        result = await self._execute_query(query, params)
        return result.data or []
    
    async def create(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Create new application"""
        # Validate required fields
        required_fields = ["user_id", "job_id", "status"]
        for field in required_fields:
            if field not in entity:
                raise ValidationError(field, None, f"Required field {field} is missing")
        
        # Add timestamps
        now = datetime.utcnow()
        entity["created_at"] = now
        entity["updated_at"] = now
        
        mutation = f"""
        INSERT INTO {self._table_name} 
        (user_id, job_id, resume_id, cover_letter, status, notes, 
         application_method, submitted_at, created_at, updated_at)
        VALUES 
        (%(user_id)s, %(job_id)s, %(resume_id)s, %(cover_letter)s, %(status)s,
         %(notes)s, %(application_method)s, %(submitted_at)s, %(created_at)s, %(updated_at)s)
        RETURNING *
        """
        
        result = await self._execute_mutation(mutation, entity)
        return result.data[0] if result.data else entity
    
    async def update(self, entity_id: str, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing application"""
        self._validate_id(entity_id)
        
        entity["updated_at"] = datetime.utcnow()
        entity["id"] = entity_id
        
        mutation = f"""
        UPDATE {self._table_name}
        SET status = %(status)s, notes = %(notes)s, 
            cover_letter = %(cover_letter)s, updated_at = %(updated_at)s
        WHERE id = %(id)s
        RETURNING *
        """
        
        result = await self._execute_mutation(mutation, entity)
        return result.data[0] if result.data else None
    
    async def delete(self, entity_id: str) -> bool:
        """Delete application by ID"""
        self._validate_id(entity_id)
        
        mutation = f"DELETE FROM {self._table_name} WHERE id = %(application_id)s"
        result = await self._execute_mutation(mutation, {"application_id": entity_id})
        return bool(result.data)
    
    async def exists(self, entity_id: str) -> bool:
        """Check if application exists"""
        self._validate_id(entity_id)
        
        query = f"SELECT 1 FROM {self._table_name} WHERE id = %(application_id)s"
        result = await self._execute_query(query, {"application_id": entity_id})
        return bool(result.data)
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count applications with optional filters"""
        query = f"SELECT COUNT(*) as count FROM {self._table_name}"
        params = {}
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = %({key})s")
                params[key] = value
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        result = await self._execute_query(query, params)
        return result.data[0]["count"] if result.data else 0
    
    async def find_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Find applications by user ID"""
        query = f"""
        SELECT a.*, j.title as job_title, j.company, j.location
        FROM {self._table_name} a
        LEFT JOIN job_listings j ON a.job_id = j.id
        WHERE a.user_id = %(user_id)s
        ORDER BY a.created_at DESC
        """
        
        result = await self._execute_query(query, {"user_id": user_id})
        return result.data or []
    
    async def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Find applications by status"""
        query = f"""
        SELECT a.*, j.title as job_title, j.company, j.location
        FROM {self._table_name} a
        LEFT JOIN job_listings j ON a.job_id = j.id
        WHERE a.status = %(status)s
        ORDER BY a.created_at DESC
        """
        
        result = await self._execute_query(query, {"status": status})
        return result.data or []
    
    async def find_by_job(self, job_id: str) -> List[Dict[str, Any]]:
        """Find applications for a specific job"""
        query = f"""
        SELECT a.*, j.title as job_title, j.company, j.location
        FROM {self._table_name} a
        LEFT JOIN job_listings j ON a.job_id = j.id
        WHERE a.job_id = %(job_id)s
        ORDER BY a.created_at DESC
        """
        
        result = await self._execute_query(query, {"job_id": job_id})
        return result.data or []
    
    async def get_application_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get application history for user"""
        query = f"""
        SELECT a.*, j.title as job_title, j.company, j.location
        FROM {self._table_name} a
        LEFT JOIN job_listings j ON a.job_id = j.id
        WHERE a.user_id = %(user_id)s
        ORDER BY a.created_at DESC
        LIMIT %(limit)s
        """
        
        result = await self._execute_query(query, {"user_id": user_id, "limit": limit})
        return result.data or []
    
    async def update_status(self, application_id: str, status: str, notes: Optional[str] = None) -> bool:
        """Update application status"""
        self._validate_id(application_id)
        
        mutation = f"""
        UPDATE {self._table_name}
        SET status = %(status)s, notes = %(notes)s, updated_at = %(updated_at)s
        WHERE id = %(application_id)s
        """
        
        params = {
            "application_id": application_id,
            "status": status,
            "notes": notes,
            "updated_at": datetime.utcnow()
        }
        
        result = await self._execute_mutation(mutation, params)
        return bool(result.data)
    
    async def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get application statistics for user"""
        query = f"""
        SELECT 
            COUNT(*) as total_applications,
            COUNT(CASE WHEN status = 'submitted' THEN 1 END) as submitted_count,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
            COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as confirmed_count,
            AVG(CASE WHEN submitted_at IS NOT NULL 
                THEN EXTRACT(EPOCH FROM (submitted_at - created_at))/3600 
                ELSE NULL END) as avg_submission_time_hours
        FROM {self._table_name}
        WHERE user_id = %(user_id)s
        """
        
        result = await self._execute_query(query, {"user_id": user_id})
        return result.data[0] if result.data else {}