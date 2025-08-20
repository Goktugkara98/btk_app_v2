# =============================================================================
# USER MODEL
# =============================================================================
# SQLAlchemy User model for authentication and user management
# =============================================================================

from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Boolean, Text, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import db

class User(db.Model):
    """User model for authentication and user management"""
    
    __tablename__ = 'users'
    
    # Primary key
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Authentication fields
    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Personal information
    first_name = Column(String(50))
    last_name = Column(String(50))
    birth_date = Column(Date)
    gender = Column(Enum('male', 'female', 'other', name='gender_enum'))
    country = Column(String(100))
    city = Column(String(100))
    school = Column(String(100))
    phone = Column(String(20))
    bio = Column(Text)
    avatar_path = Column(String(255))
    
    # Status fields
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    quiz_sessions = relationship('QuizSession', back_populates='user', cascade='all, delete-orphan')
    chat_sessions = relationship('ChatSession', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'gender': self.gender,
            'country': self.country,
            'city': self.city,
            'school': self.school,
            'phone': self.phone,
            'bio': self.bio,
            'avatar_path': self.avatar_path,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
