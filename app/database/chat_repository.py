# =============================================================================
# CHAT REPOSITORY
# =============================================================================
# Chat session ve mesaj veritabanı işlemlerini yönetir.
# =============================================================================

import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from .db_connection import DatabaseConnection

class ChatRepository:
    """
    Chat session ve mesaj veritabanı işlemlerini yönetir.
    """
    
    def __init__(self, db_connection=None):
        """Chat repository'yi başlatır."""
        self.db_connection = db_connection or DatabaseConnection()
    
    def create_chat_session(self, quiz_session_id: str, question_id: int, user_id: Optional[int] = None, context: Dict[str, Any] = None) -> str:
        """
        Yeni chat session oluşturur.
        
        Args:
            quiz_session_id: Quiz session ID
            question_id: Soru ID
            user_id: Kullanıcı ID (optional)
            context: Quiz context bilgileri
            
        Returns:
            Chat session ID
        """
        try:
            # Quiz session + question ID kombinasyonu olarak chat session ID oluştur
            chat_session_id = f"chat_{quiz_session_id}_{question_id}"
            
            with self.db_connection as conn:
                query = """
                INSERT INTO chat_sessions 
                (session_id, quiz_session_id, question_id, user_id, subject_name, topic_name, difficulty_level, last_activity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    chat_session_id,
                    quiz_session_id,
                    question_id,
                    user_id,
                    context.get('subject') if context else None,
                    context.get('topic') if context else None,
                    context.get('difficulty') if context else None,
                    datetime.now()
                )
                
                conn.cursor.execute(query, values)
                return chat_session_id
                
        except Exception as e:
            # Keep only critical error
            print(f"❌ Error creating chat session: {e}")
            raise
    
    def get_chat_session_by_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        """
        Belirli bir soru için chat session'ı getirir
        
        Args:
            question_id: Soru ID
            
        Returns:
            Chat session bilgisi veya None
        """
        try:
            with self.db_connection as conn:
                query = """
                    SELECT cs.*, qs.session_id as quiz_session_id
                    FROM chat_sessions cs
                    JOIN quiz_sessions qs ON cs.quiz_session_id = qs.id
                    WHERE cs.question_id = %s
                    ORDER BY cs.created_at DESC
                    LIMIT 1
                """
                conn.cursor.execute(query, (question_id,))
                result = conn.cursor.fetchone()
                
                if result:
                    return dict(zip([col[0] for col in conn.cursor.description], result))
                return None
                
        except Exception as e:
            return None
    
    def get_chat_messages(self, chat_session_id: str) -> List[Dict[str, Any]]:
        """
        Chat session'ına ait mesajları getirir
        
        Args:
            chat_session_id: Chat session ID (string)
            
        Returns:
            Mesajlar listesi
        """
        try:
            with self.db_connection as conn:
                query = """
                    SELECT id, chat_session_id, message_type as role, content, action_type as label, created_at
                    FROM chat_messages
                    WHERE chat_session_id = %s
                    ORDER BY created_at ASC
                """
                
                conn.cursor.execute(query, (chat_session_id,))
                results = conn.cursor.fetchall()
                
                # Since cursor is created with dictionary=True, results are already dictionaries
                messages = []
                for row in results:
                    # row is already a dictionary, no need to convert
                    messages.append(row)
                
                return messages
                
        except Exception as e:
            return []
    
    def get_chat_session(self, chat_session_id: str) -> Optional[Dict[str, Any]]:
        """
        Chat session bilgilerini döndürür.
        
        Args:
            chat_session_id: Chat session ID
            
        Returns:
            Chat session bilgileri veya None
        """
        try:
            with self.db_connection as conn:
                query = """
                SELECT cs.*, COUNT(cm.id) as message_count
                FROM chat_sessions cs
                LEFT JOIN chat_messages cm ON cs.session_id = cm.chat_session_id
                WHERE cs.session_id = %s
                GROUP BY cs.id
                """
                
                conn.cursor.execute(query, (chat_session_id,))
                result = conn.cursor.fetchone()
                
                if result:
                    return dict(result)
                    
                return None
                
        except Exception as e:
            return None
    
    def get_or_create_chat_session(self, quiz_session_id: str, question_id: int, user_id: Optional[int] = None, context: Dict[str, Any] = None) -> str:
        """
        Mevcut chat session'ı bulur veya yeni oluşturur.
        
        Args:
            quiz_session_id: Quiz session ID
            question_id: Soru ID
            user_id: Kullanıcı ID (optional)
            context: Quiz context bilgileri
            
        Returns:
            Chat session ID
        """
        try:
            # Önce mevcut session'ı ara
            with self.db_connection as conn:
                query = """
                SELECT session_id FROM chat_sessions 
                WHERE quiz_session_id = %s AND question_id = %s AND status = 'active'
                ORDER BY created_at DESC LIMIT 1
                """
                
                conn.cursor.execute(query, (quiz_session_id, question_id))
                result = conn.cursor.fetchone()
                
                if result:
                    session_id = result['session_id']
                    # Last activity'yi güncelle
                    self.update_last_activity(session_id)
                    return session_id
                else:
                    # Yeni session oluştur
                    return self.create_chat_session(quiz_session_id, question_id, user_id, context)
                    
        except Exception as e:
            # Fallback: yeni session oluştur
            return self.create_chat_session(quiz_session_id, question_id, user_id, context)
    
    def add_message(self, chat_session_id: str, message_type: str, content: str, action_type: Optional[str] = None, 
                   ai_model: Optional[str] = None, prompt_used: Optional[str] = None, 
                   response_time_ms: Optional[int] = None, metadata: Optional[Dict] = None) -> int:
        """
        Chat session'a yeni mesaj ekler.
        
        Args:
            chat_session_id: Chat session ID
            message_type: 'user', 'ai', 'system'
            content: Mesaj içeriği
            action_type: Action tipi (optional)
            ai_model: Kullanılan AI modeli (optional)
            prompt_used: AI'ya gönderilen prompt (optional)
            response_time_ms: Yanıt süresi (optional)
            metadata: Ek metadata (optional)
            
        Returns:
            Mesaj ID
        """
        try:
            with self.db_connection as conn:
                query = """
                INSERT INTO chat_messages 
                (chat_session_id, message_type, content, action_type, ai_model, prompt_used, response_time_ms, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    chat_session_id,
                    message_type,
                    content,
                    action_type,
                    ai_model,
                    prompt_used,
                    response_time_ms,
                    json.dumps(metadata) if metadata else None
                )
                
                conn.cursor.execute(query, values)
                message_id = conn.cursor.lastrowid
                
                # Last activity'yi güncelle
                self.update_last_activity(chat_session_id)
                
                return message_id
                
        except Exception as e:
            raise
    
    def get_conversation_history(self, chat_session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Chat session'ının son mesajlarını getirir.
        
        Args:
            chat_session_id: Chat session ID
            limit: Maksimum mesaj sayısı
            
        Returns:
            Mesajlar listesi
        """
        try:
            with self.db_connection as conn:
                query = """
                SELECT id, message_type as role, content, action_type, created_at
                FROM chat_messages
                WHERE chat_session_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """
                
                conn.cursor.execute(query, (chat_session_id, limit))
                results = conn.cursor.fetchall()
                
                messages = []
                for row in results:
                    messages.append(dict(zip([col[0] for col in conn.cursor.description], row)))
                
                return messages[::-1]  # Chronological order
                
        except Exception as e:
            return []
    
    def update_last_activity(self, chat_session_id: str):
        """Chat session'ının son aktivite zamanını günceller."""
        try:
            with self.db_connection as conn:
                query = "UPDATE chat_sessions SET last_activity = %s WHERE session_id = %s"
                conn.cursor.execute(query, (datetime.now(), chat_session_id))
                
        except Exception as e:
            pass
    
    def update_session_stats(self, chat_session_id: str):
        """Chat session istatistiklerini günceller."""
        try:
            with self.db_connection as conn:
                # Mesaj sayısını hesapla
                query = """
                UPDATE chat_sessions cs
                SET message_count = (
                    SELECT COUNT(*) FROM chat_messages cm 
                    WHERE cm.chat_session_id = cs.session_id
                )
                WHERE cs.session_id = %s
                """
                conn.cursor.execute(query, (chat_session_id,))
                
        except Exception as e:
            pass
    
    def close_chat_session(self, chat_session_id: str):
        """Chat session'ını kapatır."""
        try:
            with self.db_connection as conn:
                query = "UPDATE chat_sessions SET status = 'closed', closed_at = %s WHERE session_id = %s"
                conn.cursor.execute(query, (datetime.now(), chat_session_id))
                
        except Exception as e:
            pass
    
    def cleanup_old_sessions(self, hours: int = 24):
        """Eski chat session'larını temizler."""
        try:
            with self.db_connection as conn:
                cutoff_time = datetime.now() - timedelta(hours=hours)
                query = "DELETE FROM chat_sessions WHERE created_at < %s AND status = 'closed'"
                conn.cursor.execute(query, (cutoff_time,))
                deleted_count = conn.cursor.rowcount
                
        except Exception as e:
            pass
    
    def get_session_statistics(self, chat_session_id: str) -> Dict[str, Any]:
        """
        Chat session istatistiklerini döndürür.
        
        Args:
            chat_session_id: Chat session ID
            
        Returns:
            İstatistikler dictionary
        """
        try:
            with self.db_connection as conn:
                query = """
                SELECT 
                    COUNT(*) as total_messages,
                    COUNT(CASE WHEN message_type = 'user' THEN 1 END) as user_messages,
                    COUNT(CASE WHEN message_type = 'ai' THEN 1 END) as ai_messages,
                    COUNT(CASE WHEN message_type = 'system' THEN 1 END) as system_messages,
                    AVG(response_time_ms) as avg_response_time,
                    MIN(created_at) as first_message,
                    MAX(created_at) as last_message
                FROM chat_messages
                WHERE chat_session_id = %s
                """
                
                conn.cursor.execute(query, (chat_session_id,))
                result = conn.cursor.fetchone()
                
                if result:
                    return dict(zip([col[0] for col in conn.cursor.description], result))
                return {}
                
        except Exception as e:
            return {}
