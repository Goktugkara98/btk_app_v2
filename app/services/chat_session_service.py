# =============================================================================
# CHAT SESSION SERVICE
# =============================================================================
# Bu modül, AI sohbet oturumlarını yönetir.
# Session state, context ve conversation history'yi takip eder.
# =============================================================================

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class ChatSessionService:
    """
    AI sohbet oturumlarını yöneten servis.
    Veritabanı tabanlı session management ve conversation history.
    """
    
    def __init__(self, db_connection=None):
        """Chat session servisini başlatır."""
        self.db_connection = db_connection
        
        # Chat repository'yi import et
        try:
            from app.database.chat_repository import ChatRepository
            self.chat_repo = ChatRepository(db_connection) if db_connection else None
        except ImportError as e:
            self.chat_repo = None
        
        # Context templates
        self.context_templates = {
            'educational_intro': (
                "Sen Daima adında yardımcı bir AI öğretmensin. "
                "Öğrencilere quiz sorularında yardım ediyorsun. "
                "Açıklamalarını basit, anlaşılır ve eğitici yapmalısın."
            ),
            'question_context': (
                "Öğrenci şu anda {subject} dersinin {topic} konusunda "
                "{difficulty} seviyesinde bir soru çözüyor."
            ),
            'help_context': (
                "Öğrenci bu soru hakkında yardım istiyor. "
                "Doğrudan cevap verme, ipucu ve rehberlik et."
            )
        }
    
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
            # Veritabanı tabanlı - mevcut session'ı al veya yeni oluştur
            return self.chat_repo.get_or_create_chat_session(quiz_session_id, question_id, user_id, user_context)
        else:
            # Fallback: In-memory (deprecated)
            chat_session_id = f"chat_{quiz_session_id}_{question_id}_{datetime.now().timestamp()}"
            return chat_session_id
    
    def get_session(self, chat_session_id: str) -> Optional[Dict[str, Any]]:
        """Chat session bilgilerini döndürür."""
        if self.chat_repo:
            return self.chat_repo.get_chat_session(chat_session_id)
        else:
            # Fallback: In-memory (deprecated)
            return None
    
    def update_question_context(self, chat_session_id: str, question_id: int, question_data: Dict[str, Any]):
        """
        Session'daki aktif soru context'ini günceller.
        
        Args:
            chat_session_id: Chat session ID
            question_id: Soru ID
            question_data: Soru bilgileri
        """
        if chat_session_id in self.sessions:
            self.sessions[chat_session_id]['current_question_id'] = question_id
            self.sessions[chat_session_id]['current_question_data'] = question_data
            self.sessions[chat_session_id]['last_activity'] = datetime.now()
    
    def add_message(self, chat_session_id: str, message_type: str, content: str, action_type: Optional[str] = None, 
                   ai_model: Optional[str] = None, prompt_used: Optional[str] = None, 
                   response_time_ms: Optional[int] = None, metadata: Optional[Dict] = None) -> Optional[int]:
        """
        Session'a yeni mesaj ekler.
        
        Args:
            chat_session_id: Chat session ID
            message_type: 'user', 'ai', 'system'
            content: Mesaj içeriği
            action_type: Action tipi (optional)
            ai_model: Kullanılan AI modeli (optional)
            prompt_used: AI'ya gönderilen prompt (optional)
            response_time_ms: Yanıt süresi (optional)
            metadata: Ek bilgiler (optional)
            
        Returns:
            Message ID veya None
        """
        if self.chat_repo:
            try:
                return self.chat_repo.add_message(
                    chat_session_id, message_type, content, action_type, 
                    ai_model, prompt_used, response_time_ms, metadata
                )
            except Exception as e:
                return None
        else:
            # Fallback: In-memory (deprecated)
            return None
    
    def get_conversation_context(self, chat_session_id: str, question_id: Optional[int] = None) -> str:
        """
        Mevcut conversation için context oluşturur.
        
        Args:
            chat_session_id: Chat session ID
            question_id: Spesifik soru ID (optional)
            
        Returns:
            Context string
        """
        session = self.get_session(chat_session_id)
        if not session:
            return self.context_templates['educational_intro']
        
        context_parts = [self.context_templates['educational_intro']]
        
        # Session'dan context bilgilerini al
        subject = session.get('subject_name', 'Bu ders')
        topic = session.get('topic_name', 'bu konu')
        difficulty = session.get('difficulty_level', 'orta')
        
        if subject or topic:
            context_parts.append(
                self.context_templates['question_context'].format(
                    subject=subject,
                    topic=topic,
                    difficulty=difficulty
                )
            )
        
        # Son birkaç mesajı veritabanından al (token limitini aşmamak için sadece son 2 mesaj)
        if self.chat_repo:
            recent_messages = self.chat_repo.get_conversation_history(chat_session_id, limit=3)
            if recent_messages:
                context_parts.append("\nSon sohbet:")
                for msg in recent_messages[-2:]:  # Son 2 mesaj (token limitini aşmamak için)
                    # Mesaj içeriğini kısalt (maksimum 200 karakter)
                    content = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
                    context_parts.append(f"{msg['role']}: {content}")
        
        return "\n\n".join(context_parts)
    
    def build_prompt(self, chat_session_id: str, user_message: str, action_type: str = 'general') -> str:
        """
        Kullanıcı mesajı için Gemini'ye gönderilecek prompt oluşturur.
        
        Args:
            chat_session_id: Chat session ID
            user_message: Kullanıcı mesajı
            action_type: 'general', 'explain', 'hint'
            
        Returns:
            Gemini için hazırlanmış prompt
        """
        context = self.get_conversation_context(chat_session_id)
        
        if action_type == 'explain':
            prompt = f"{context}\n\n{self.context_templates['help_context']}\n\nÖğrenci soruyu açıklamanı istiyor: {user_message}"
        elif action_type == 'hint':
            prompt = f"{context}\n\n{self.context_templates['help_context']}\n\nÖğrenci ipucu istiyor: {user_message}"
        else:
            prompt = f"{context}\n\nÖğrenci mesajı: {user_message}"
        
        return prompt
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """
        Eski session'ları temizler.
        
        Args:
            max_age_hours: Maksimum session yaşı (saat)
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for session_id, session_data in self.sessions.items():
            if session_data['last_activity'] < cutoff_time:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.sessions[session_id]
    
    def get_session_stats(self, chat_session_id: str) -> Dict[str, Any]:
        """
        Session istatistiklerini döndürür.
        
        Args:
            chat_session_id: Chat session ID
            
        Returns:
            Session istatistikleri
        """
        session = self.get_session(chat_session_id)
        if not session:
            return {}
        
        history = session['conversation_history']
        
        return {
            'total_messages': len(history),
            'user_messages': len([m for m in history if m['type'] == 'user']),
            'ai_messages': len([m for m in history if m['type'] == 'ai']),
            'session_duration': (datetime.now() - session['created_at']).total_seconds(),
            'last_activity': session['last_activity'].isoformat(),
            'status': session['status']
        }