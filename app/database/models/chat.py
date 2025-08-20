# =============================================================================
# CHAT MODELS
# =============================================================================
# SQLAlchemy ChatSession and ChatMessage models for AI chat functionality
# =============================================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import db

class ChatSession(db.Model):
    """ChatSession model for AI chat sessions"""
    
    __tablename__ = 'chat_sessions'
    
    # Primary key
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Session information
    session_name = Column(String(100))
    chat_type = Column(Enum('quiz_help', 'general', 'homework', name='chat_type_enum'), default='general')
    is_active = Column(Boolean, default=True)
    
    # Context and metadata
    context_data = Column(JSON)  # Store chat context as JSON
    session_settings = Column(JSON)  # Store chat settings as JSON
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    quiz_session_id = Column(Integer, ForeignKey('quiz_sessions.session_id'))
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    last_activity = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    user = relationship('User', back_populates='chat_sessions')
    quiz_session = relationship('QuizSession')
    messages = relationship('ChatMessage', back_populates='chat_session', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}: {self.session_name}>'
    
    def to_dict(self):
        """Convert chat session to dictionary"""
        return {
            'session_id': self.session_id,
            'session_name': self.session_name,
            'chat_type': self.chat_type,
            'is_active': self.is_active,
            'context_data': self.context_data,
            'session_settings': self.session_settings,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'quiz_session_id': self.quiz_session_id,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }

class ChatMessage(db.Model):
    """ChatMessage model for individual chat messages"""
    
    __tablename__ = 'chat_messages'
    
    # Primary key
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Message content
    message_text = Column(Text, nullable=False)
    message_type = Column(Enum('user', 'assistant', 'system', name='message_type_enum'), nullable=False)
    
    # Message metadata
    role = Column(String(50))  # User role or AI role
    tokens_used = Column(Integer, default=0)
    response_time_ms = Column(Integer, default=0)
    
    # AI-specific fields
    ai_model = Column(String(100))
    ai_confidence = Column(Float)
    ai_metadata = Column(JSON)
    
    # Foreign keys
    session_id = Column(Integer, ForeignKey('chat_sessions.session_id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    chat_session = relationship('ChatSession', back_populates='messages')
    
    def __repr__(self):
        return f'<ChatMessage {self.message_id}: {self.message_text[:30]}...>'
    
    def to_dict(self):
        """Convert chat message to dictionary"""
        return {
            'message_id': self.message_id,
            'message_text': self.message_text,
            'message_type': self.message_type,
            'role': self.role,
            'tokens_used': self.tokens_used,
            'response_time_ms': self.response_time_ms,
            'ai_model': self.ai_model,
            'ai_confidence': self.ai_confidence,
            'ai_metadata': self.ai_metadata,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
