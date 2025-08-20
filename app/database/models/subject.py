# =============================================================================
# SUBJECT MODEL
# =============================================================================
# SQLAlchemy Subject model for educational subjects
# =============================================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import db

class Subject(db.Model):
    """Subject model for educational subjects"""
    
    __tablename__ = 'subjects'
    
    # Primary key
    subject_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Subject information
    subject_name = Column(String(100), nullable=False)
    subject_code = Column(String(20), unique=True)
    description = Column(Text)
    
    # Foreign keys
    grade_id = Column(Integer, ForeignKey('grades.grade_id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    grade = relationship('Grade', back_populates='subjects')
    units = relationship('Unit', back_populates='subject', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Subject {self.subject_name}>'
    
    def to_dict(self):
        """Convert subject to dictionary"""
        return {
            'subject_id': self.subject_id,
            'subject_name': self.subject_name,
            'subject_code': self.subject_code,
            'description': self.description,
            'grade_id': self.grade_id,
            'grade_name': self.grade.grade_name if self.grade else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
