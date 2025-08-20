# =============================================================================
# TOPIC MODEL
# =============================================================================
# SQLAlchemy Topic model for educational topics
# =============================================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import db

class Topic(db.Model):
    """Topic model for educational topics"""
    
    __tablename__ = 'topics'
    
    # Primary key
    topic_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Topic information
    topic_name = Column(String(100), nullable=False)
    topic_number = Column(Integer, nullable=False)
    description = Column(Text)
    
    # Foreign keys
    unit_id = Column(Integer, ForeignKey('units.unit_id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    unit = relationship('Unit', back_populates='topics')
    questions = relationship('Question', back_populates='topic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Topic {self.topic_name}>'
    
    def to_dict(self):
        """Convert topic to dictionary"""
        return {
            'topic_id': self.topic_id,
            'topic_name': self.topic_name,
            'topic_number': self.topic_number,
            'description': self.description,
            'unit_id': self.unit_id,
            'unit_name': self.unit.unit_name if self.unit else None,
            'subject_name': self.unit.subject.subject_name if self.unit and self.unit.subject else None,
            'grade_name': self.unit.subject.grade.grade_name if self.unit and self.unit.subject and self.unit.subject.grade else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
