# =============================================================================
# UNIT MODEL
# =============================================================================
# SQLAlchemy Unit model for educational units
# =============================================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import db

class Unit(db.Model):
    """Unit model for educational units"""
    
    __tablename__ = 'units'
    
    # Primary key
    unit_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Unit information
    unit_name = Column(String(100), nullable=False)
    unit_number = Column(Integer, nullable=False)
    description = Column(Text)
    
    # Foreign keys
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    subject = relationship('Subject', back_populates='units')
    topics = relationship('Topic', back_populates='unit', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Unit {self.unit_name}>'
    
    def to_dict(self):
        """Convert unit to dictionary"""
        return {
            'unit_id': self.unit_id,
            'unit_name': self.unit_name,
            'unit_number': self.unit_number,
            'description': self.description,
            'subject_id': self.subject_id,
            'subject_name': self.subject.subject_name if self.subject else None,
            'grade_name': self.subject.grade.grade_name if self.subject and self.subject.grade else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
