# =============================================================================
# QUESTION MODELS
# =============================================================================
# SQLAlchemy Question and QuestionOption models for quiz questions
# =============================================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import db

class Question(db.Model):
    """Question model for quiz questions"""
    
    __tablename__ = 'questions'
    
    # Primary key
    question_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum('multiple_choice', 'true_false', 'open_ended', name='question_type_enum'), nullable=False)
    difficulty_level = Column(Enum('easy', 'medium', 'hard', name='difficulty_level_enum'), default='medium')
    
    # Explanation and metadata
    explanation = Column(Text)
    tags = Column(String(255))
    
    # Foreign keys
    topic_id = Column(Integer, ForeignKey('topics.topic_id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    topic = relationship('Topic', back_populates='questions')
    options = relationship('QuestionOption', back_populates='question', cascade='all, delete-orphan')
    quiz_session_questions = relationship('QuizSessionQuestion', back_populates='question', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.question_id}: {self.question_text[:50]}...>'
    
    def to_dict(self):
        """Convert question to dictionary"""
        return {
            'question_id': self.question_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'difficulty_level': self.difficulty_level,
            'explanation': self.explanation,
            'tags': self.tags,
            'topic_id': self.topic_id,
            'topic_name': self.topic.topic_name if self.topic else None,
            'unit_name': self.topic.unit.unit_name if self.topic and self.topic.unit else None,
            'subject_name': self.topic.unit.subject.subject_name if self.topic and self.topic.unit and self.topic.unit.subject else None,
            'grade_name': self.topic.unit.subject.grade.grade_name if self.topic and self.topic.unit and self.topic.unit.subject and self.topic.unit.subject.grade else None,
            'options': [option.to_dict() for option in self.options],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class QuestionOption(db.Model):
    """QuestionOption model for question answer choices"""
    
    __tablename__ = 'question_options'
    
    # Primary key
    option_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Option content
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    option_order = Column(Integer, default=0)
    
    # Foreign keys
    question_id = Column(Integer, ForeignKey('questions.question_id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    question = relationship('Question', back_populates='options')
    
    def __repr__(self):
        return f'<QuestionOption {self.option_id}: {self.option_text[:30]}...>'
    
    def to_dict(self):
        """Convert option to dictionary"""
        return {
            'option_id': self.option_id,
            'option_text': self.option_text,
            'is_correct': self.is_correct,
            'option_order': self.option_order,
            'question_id': self.question_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
