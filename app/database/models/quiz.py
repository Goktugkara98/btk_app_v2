# =============================================================================
# QUIZ MODELS
# =============================================================================
# SQLAlchemy QuizSession and QuizSessionQuestion models for quiz sessions
# =============================================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import db

class QuizSession(db.Model):
    """QuizSession model for quiz sessions"""
    
    __tablename__ = 'quiz_sessions'
    
    # Primary key
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Session information
    session_name = Column(String(100))
    quiz_mode = Column(Enum('practice', 'exam', 'timed', name='quiz_mode_enum'), default='practice')
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    score_percentage = Column(Float, default=0.0)
    
    # Session state
    is_completed = Column(Boolean, default=False)
    start_time = Column(DateTime, default=func.current_timestamp())
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Settings and metadata
    settings = Column(JSON)  # Store quiz settings as JSON
    notes = Column(Text)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    grade_id = Column(Integer, ForeignKey('grades.grade_id'))
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'))
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    user = relationship('User', back_populates='quiz_sessions')
    grade = relationship('Grade')
    subject = relationship('Subject')
    session_questions = relationship('QuizSessionQuestion', back_populates='quiz_session', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<QuizSession {self.session_id}: {self.session_name}>'
    
    def to_dict(self):
        """Convert quiz session to dictionary"""
        return {
            'session_id': self.session_id,
            'session_name': self.session_name,
            'quiz_mode': self.quiz_mode,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'score_percentage': self.score_percentage,
            'is_completed': self.is_completed,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'settings': self.settings,
            'notes': self.notes,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'grade_id': self.grade_id,
            'grade_name': self.grade.grade_name if self.grade else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.subject_name if self.subject else None,
            'session_questions': [sq.to_dict() for sq in self.session_questions],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class QuizSessionQuestion(db.Model):
    """QuizSessionQuestion model for questions in quiz sessions"""
    
    __tablename__ = 'quiz_session_questions'
    
    # Primary key
    session_question_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Question state
    question_order = Column(Integer, nullable=False)
    is_answered = Column(Boolean, default=False)
    is_correct = Column(Boolean)
    selected_option_id = Column(Integer)
    time_spent_seconds = Column(Integer, default=0)
    
    # User response
    user_answer = Column(Text)
    user_explanation = Column(Text)
    
    # Foreign keys
    session_id = Column(Integer, ForeignKey('quiz_sessions.session_id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.question_id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    quiz_session = relationship('QuizSession', back_populates='session_questions')
    question = relationship('Question', back_populates='quiz_session_questions')
    
    def __repr__(self):
        return f'<QuizSessionQuestion {self.session_question_id}: Q{self.question_order}>'
    
    def to_dict(self):
        """Convert session question to dictionary"""
        return {
            'session_question_id': self.session_question_id,
            'question_order': self.question_order,
            'is_answered': self.is_answered,
            'is_correct': self.is_correct,
            'selected_option_id': self.selected_option_id,
            'time_spent_seconds': self.time_spent_seconds,
            'user_answer': self.user_answer,
            'user_explanation': self.user_explanation,
            'session_id': self.session_id,
            'question_id': self.question_id,
            'question': self.question.to_dict() if self.question else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
