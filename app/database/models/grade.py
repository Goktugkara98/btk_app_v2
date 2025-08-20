# =============================================================================
# GRADE MODEL
# =============================================================================
# SQLAlchemy Grade model for educational grade levels
# =============================================================================

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import db

class Grade(db.Model):
    """Grade model for educational grade levels"""
    
    __tablename__ = 'grades'
    
    # Primary key
    grade_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Grade information
    grade_name = Column(String(50), nullable=False, unique=True)
    grade_number = Column(Integer, nullable=False, unique=True)
    description = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    subjects = relationship('Subject', back_populates='grade', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Grade {self.grade_name}>'
    
    def to_dict(self):
        """Convert grade to dictionary"""
        return {
            'grade_id': self.grade_id,
            'grade_name': self.grade_name,
            'grade_number': self.grade_number,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
