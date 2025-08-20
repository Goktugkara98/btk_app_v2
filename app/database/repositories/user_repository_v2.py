# =============================================================================
# USER REPOSITORY V2 - SQLALCHEMY
# =============================================================================
# Modern SQLAlchemy-based user repository with advanced user management
# =============================================================================

from typing import Optional, List, Dict, Any
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from .base_repository_v2 import BaseRepository
from ..models.user import User

class UserRepository(BaseRepository[User]):
    """User repository with advanced user management features"""
    
    def __init__(self):
        """Initialize user repository"""
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username to search for
            
        Returns:
            User instance or None if not found
        """
        return self.get_by_field('username', username)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: Email to search for
            
        Returns:
            User instance or None if not found
        """
        return self.get_by_field('email', email)
    
    def get_active_users(self, limit: Optional[int] = None) -> List[User]:
        """
        Get all active users
        
        Args:
            limit: Maximum number of users to return
            
        Returns:
            List of active users
        """
        return self.find({'is_active': True}, limit=limit)
    
    def get_admin_users(self, limit: Optional[int] = None) -> List[User]:
        """
        Get all admin users
        
        Args:
            limit: Maximum number of users to return
            
        Returns:
            List of admin users
        """
        return self.find({'is_admin': True}, limit=limit)
    
    def search_users(self, search_term: str, limit: Optional[int] = None) -> List[User]:
        """
        Search users by name, username, or email
        
        Args:
            search_term: Text to search for
            limit: Maximum number of users to return
            
        Returns:
            List of matching users
        """
        search_fields = ['username', 'email', 'first_name', 'last_name']
        return self.search(search_term, search_fields, limit)
    
    def get_users_by_grade(self, grade_id: int, limit: Optional[int] = None) -> List[User]:
        """
        Get users by grade (if grade tracking is implemented)
        
        Args:
            grade_id: Grade ID to filter by
            limit: Maximum number of users to return
            
        Returns:
            List of users in specified grade
        """
        # This would need to be implemented based on your user-grade relationship
        # For now, returning empty list as placeholder
        return []
    
    def get_users_by_subject(self, subject_id: int, limit: Optional[int] = None) -> List[User]:
        """
        Get users by subject (if subject tracking is implemented)
        
        Args:
            subject_id: Subject ID to filter by
            limit: Maximum number of users to return
            
        Returns:
            List of users studying specified subject
        """
        # This would need to be implemented based on your user-subject relationship
        # For now, returning empty list as placeholder
        return []
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[User]:
        """
        Update user profile information
        
        Args:
            user_id: User ID to update
            profile_data: Dictionary of profile fields to update
            
        Returns:
            Updated user instance or None if failed
        """
        # Filter out sensitive fields that shouldn't be updated via profile
        allowed_fields = {
            'first_name', 'last_name', 'birth_date', 'gender', 'country', 
            'city', 'school', 'phone', 'bio', 'avatar_path'
        }
        
        filtered_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
        
        if not filtered_data:
            return None
        
        return self.update(user_id, **filtered_data)
    
    def update_user_password(self, user_id: int, new_password_hash: str) -> Optional[User]:
        """
        Update user password
        
        Args:
            user_id: User ID to update
            new_password_hash: New hashed password
            
        Returns:
            Updated user instance or None if failed
        """
        return self.update(user_id, password_hash=new_password_hash)
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """
        Deactivate a user account
        
        Args:
            user_id: User ID to deactivate
            
        Returns:
            Updated user instance or None if failed
        """
        return self.update(user_id, is_active=False)
    
    def activate_user(self, user_id: int) -> Optional[User]:
        """
        Activate a user account
        
        Args:
            user_id: User ID to activate
            
        Returns:
            Updated user instance or None if failed
        """
        return self.update(user_id, is_active=True)
    
    def promote_to_admin(self, user_id: int) -> Optional[User]:
        """
        Promote user to admin
        
        Args:
            user_id: User ID to promote
            
        Returns:
            Updated user instance or None if failed
        """
        return self.update(user_id, is_admin=True)
    
    def demote_from_admin(self, user_id: int) -> Optional[User]:
        """
        Remove admin privileges from user
        
        Args:
            user_id: User ID to demote
            
        Returns:
            Updated user instance or None if failed
        """
        return self.update(user_id, is_admin=False)
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get user statistics and activity data
        
        Args:
            user_id: User ID to get statistics for
            
        Returns:
            Dictionary with user statistics
        """
        try:
            session = self.get_session()
            user = session.query(User).filter_by(user_id=user_id).first()
            
            if not user:
                return {}
            
            # Get quiz session statistics
            quiz_sessions = session.query(user.quiz_sessions).all()
            total_quizzes = len(quiz_sessions)
            completed_quizzes = len([qs for qs in quiz_sessions if qs.is_completed])
            average_score = sum([qs.score_percentage for qs in quiz_sessions if qs.is_completed]) / completed_quizzes if completed_quizzes > 0 else 0
            
            # Get chat session statistics
            chat_sessions = session.query(user.chat_sessions).all()
            total_chats = len(chat_sessions)
            
            return {
                'user_id': user_id,
                'username': user.username,
                'total_quizzes': total_quizzes,
                'completed_quizzes': completed_quizzes,
                'average_score': round(average_score, 2),
                'total_chats': total_chats,
                'account_age_days': (user.created_at - user.created_at).days if user.created_at else 0,
                'last_activity': user.updated_at.isoformat() if user.updated_at else None
            }
        except SQLAlchemyError as e:
            print(f"Error getting user statistics: {e}")
            return {}
    
    def get_users_by_activity(self, days: int = 30, limit: Optional[int] = None) -> List[User]:
        """
        Get users by recent activity
        
        Args:
            days: Number of days to look back for activity
            limit: Maximum number of users to return
            
        Returns:
            List of active users
        """
        try:
            session = self.get_session()
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get users with recent quiz sessions or chat activity
            query = session.query(User).join(User.quiz_sessions).filter(
                or_(
                    User.quiz_sessions.any(QuizSession.updated_at >= cutoff_date),
                    User.chat_sessions.any(ChatSession.last_activity >= cutoff_date)
                )
            ).distinct()
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error getting users by activity: {e}")
            return []
    
    def bulk_update_user_status(self, user_ids: List[int], is_active: bool) -> int:
        """
        Bulk update user active status
        
        Args:
            user_ids: List of user IDs to update
            is_active: New active status
            
        Returns:
            Number of updated users
        """
        return self.bulk_update(user_ids, {'is_active': is_active})
    
    def get_user_export_data(self, user_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Get user data for export (CSV, Excel, etc.)
        
        Args:
            user_ids: Optional list of user IDs to export, if None exports all
            
        Returns:
            List of user dictionaries for export
        """
        try:
            if user_ids:
                users = [self.get_by_id(uid) for uid in user_ids if self.get_by_id(uid)]
            else:
                users = self.get_all()
            
            export_data = []
            for user in users:
                if user:
                    export_data.append({
                        'user_id': user.user_id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'birth_date': user.birth_date.isoformat() if user.birth_date else '',
                        'gender': user.gender or '',
                        'country': user.country or '',
                        'city': user.city or '',
                        'school': user.school or '',
                        'phone': user.phone or '',
                        'is_active': user.is_active,
                        'is_admin': user.is_admin,
                        'created_at': user.created_at.isoformat() if user.created_at else '',
                        'updated_at': user.updated_at.isoformat() if user.updated_at else ''
                    })
            
            return export_data
        except SQLAlchemyError as e:
            print(f"Error getting user export data: {e}")
            return []
