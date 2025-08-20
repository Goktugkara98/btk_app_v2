# =============================================================================
# BASE REPOSITORY V2 - SQLALCHEMY
# =============================================================================
# Modern SQLAlchemy-based base repository with common CRUD operations
# =============================================================================

from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from ..database import db

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository class for SQLAlchemy models"""
    
    def __init__(self, model: Type[T]):
        """
        Initialize repository with model class
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
        self.db = db
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.db.session
    
    def create(self, **kwargs) -> Optional[T]:
        """
        Create a new record
        
        Args:
            **kwargs: Model attributes
            
        Returns:
            Created model instance or None if failed
        """
        try:
            session = self.get_session()
            instance = self.model(**kwargs)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error creating {self.model.__name__}: {e}")
            return None
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Get record by ID
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None if not found
        """
        try:
            session = self.get_session()
            return session.query(self.model).filter_by(id=id).first()
        except SQLAlchemyError as e:
            print(f"Error getting {self.model.__name__} by ID: {e}")
            return None
    
    def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """
        Get record by specific field value
        
        Args:
            field: Field name
            value: Field value
            
        Returns:
            Model instance or None if not found
        """
        try:
            session = self.get_session()
            filter_kwargs = {field: value}
            return session.query(self.model).filter_by(**filter_kwargs).first()
        except SQLAlchemyError as e:
            print(f"Error getting {self.model.__name__} by {field}: {e}")
            return None
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        Get all records with optional pagination
        
        Args:
            limit: Maximum number of records
            offset: Number of records to skip
            
        Returns:
            List of model instances
        """
        try:
            session = self.get_session()
            query = session.query(self.model)
            
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error getting all {self.model.__name__}: {e}")
            return []
    
    def find(self, filters: Dict[str, Any], limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        Find records by multiple filters
        
        Args:
            filters: Dictionary of field-value pairs
            limit: Maximum number of records
            offset: Number of records to skip
            
        Returns:
            List of model instances
        """
        try:
            session = self.get_session()
            query = session.query(self.model)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
            
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error finding {self.model.__name__}: {e}")
            return []
    
    def search(self, search_term: str, search_fields: List[str], limit: Optional[int] = None) -> List[T]:
        """
        Search records by text in specified fields
        
        Args:
            search_term: Text to search for
            search_fields: List of field names to search in
            limit: Maximum number of records
            
        Returns:
            List of model instances
        """
        try:
            session = self.get_session()
            query = session.query(self.model)
            
            # Build search conditions
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    search_conditions.append(
                        getattr(self.model, field).ilike(f"%{search_term}%")
                    )
            
            if search_conditions:
                query = query.filter(or_(*search_conditions))
            
            if limit:
                query = query.limit(limit)
                
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error searching {self.model.__name__}: {e}")
            return []
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """
        Update record by ID
        
        Args:
            id: Record ID
            **kwargs: Fields to update
            
        Returns:
            Updated model instance or None if failed
        """
        try:
            session = self.get_session()
            instance = session.query(self.model).filter_by(id=id).first()
            
            if not instance:
                return None
            
            # Update fields
            for field, value in kwargs.items():
                if hasattr(instance, field):
                    setattr(instance, field, value)
            
            session.commit()
            session.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating {self.model.__name__}: {e}")
            return None
    
    def delete(self, id: int) -> bool:
        """
        Delete record by ID
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            session = self.get_session()
            instance = session.query(self.model).filter_by(id=id).first()
            
            if not instance:
                return False
            
            session.delete(instance)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting {self.model.__name__}: {e}")
            return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters
        
        Args:
            filters: Optional dictionary of field-value pairs
            
        Returns:
            Number of records
        """
        try:
            session = self.get_session()
            query = session.query(self.model)
            
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.filter(getattr(self.model, field) == value)
            
            return query.count()
        except SQLAlchemyError as e:
            print(f"Error counting {self.model.__name__}: {e}")
            return 0
    
    def exists(self, filters: Dict[str, Any]) -> bool:
        """
        Check if record exists with given filters
        
        Args:
            filters: Dictionary of field-value pairs
            
        Returns:
            True if exists, False otherwise
        """
        return self.count(filters) > 0
    
    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple records at once
        
        Args:
            data_list: List of dictionaries with model attributes
            
        Returns:
            List of created model instances
        """
        try:
            session = self.get_session()
            instances = []
            
            for data in data_list:
                instance = self.model(**data)
                instances.append(instance)
                session.add(instance)
            
            session.commit()
            
            # Refresh all instances
            for instance in instances:
                session.refresh(instance)
            
            return instances
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error bulk creating {self.model.__name__}: {e}")
            return []
    
    def bulk_update(self, id_list: List[int], update_data: Dict[str, Any]) -> int:
        """
        Update multiple records at once
        
        Args:
            id_list: List of record IDs to update
            update_data: Dictionary of fields to update
            
        Returns:
            Number of updated records
        """
        try:
            session = self.get_session()
            updated_count = session.query(self.model).filter(
                self.model.id.in_(id_list)
            ).update(update_data, synchronize_session=False)
            
            session.commit()
            return updated_count
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error bulk updating {self.model.__name__}: {e}")
            return 0
    
    def get_paginated(self, page: int = 1, per_page: int = 20, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get paginated results
        
        Args:
            page: Page number (1-based)
            per_page: Number of records per page
            filters: Optional dictionary of field-value pairs
            
        Returns:
            Dictionary with pagination info and data
        """
        try:
            total_count = self.count(filters)
            offset = (page - 1) * per_page
            
            data = self.find(filters, limit=per_page, offset=offset)
            
            total_pages = (total_count + per_page - 1) // per_page
            
            return {
                'data': data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
        except SQLAlchemyError as e:
            print(f"Error getting paginated {self.model.__name__}: {e}")
            return {'data': [], 'pagination': {}}
