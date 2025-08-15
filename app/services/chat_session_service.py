# =============================================================================
# CHAT SESSION SERVICE - CLEAN VERSION
# =============================================================================
# Bu modül sadece AI sohbet oturumlarının yönetimini yapar.
# Session lifecycle, stats ve temel repository işlemleri.
# =============================================================================

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class ChatSessionService:
    """
    AI sohbet oturumlarının yaşam döngüsünü yöneten servis.
    Sadece session management - mesaj işleme ChatMessageService'te.
    """
    
    def __init__(self, db_connection=None):
        """Chat session servisini başlatır."""
        self.db_connection = db_connection
        
        # Chat repository'yi import et
        try:
            from app.database.repositories.chat_repository import ChatRepository
            self.chat_repo = ChatRepository(db_connection) if db_connection else None
        except ImportError as e:
            self.chat_repo = None
    
    # =============================================================================
    # CORE SESSION MANAGEMENT
    # =============================================================================
    
    def create_session_for_question(self, quiz_session_id: str, question_id: int, user_context: Dict[str, Any], user_id: Optional[int] = None) -> str:
        """
        Belirli bir soru için chat session oluşturur.
        
        Args:
            quiz_session_id: Quiz session ID
            question_id: Soru ID
            user_context: Kullanıcı ve quiz bilgileri
            user_id: Kullanıcı ID (optional)
            
        Returns:
            Chat session ID
        """
        if self.chat_repo:
            return self.chat_repo.get_or_create_chat_session(quiz_session_id, question_id, user_id, user_context)
        else:
            # Fallback: Simple ID generation
            chat_session_id = f"chat_{quiz_session_id}_{question_id}_{datetime.now().timestamp()}"
            return chat_session_id
    
    def get_session(self, chat_session_id: str) -> Optional[Dict[str, Any]]:
        """Chat session bilgilerini döndürür."""
        if self.chat_repo:
            return self.chat_repo.get_chat_session(chat_session_id)
        return None
    
    
    # =============================================================================
    # SESSION STATISTICS AND UTILITIES
    # =============================================================================
    
    def get_session_stats(self, chat_session_id: str) -> Dict[str, Any]:
        """Chat session istatistiklerini döndürür."""
        if not self.chat_repo:
            return {}
        
        try:
            messages = self.chat_repo.get_conversation_history(chat_session_id)
            user_messages = len([m for m in messages if m.get('role') == 'user'])
            ai_messages = len([m for m in messages if m.get('role') == 'ai'])
            system_messages = len([m for m in messages if m.get('role') == 'system'])
            
            return {
                'total_messages': len(messages),
                'user_messages': user_messages,
                'ai_messages': ai_messages,
                'system_messages': system_messages,
                'last_activity': messages[-1].get('created_at') if messages else None
            }
        except Exception:
            return {}
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Eski session'ları temizler.
        
        Args:
            max_age_hours: Maksimum session yaşı (saat)
            
        Returns:
            Temizlenen session sayısı
        """
        if not self.chat_repo:
            return 0
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            return self.chat_repo.cleanup_old_sessions(cutoff_time)
        except Exception:
            return 0