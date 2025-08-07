# =============================================================================
# CHAT MESSAGE SERVICE
# =============================================================================
# Bu modül, AI sohbet mesajlarının işlenmesi ve formatlanmasını yönetir.
# Mesaj validasyonu, format dönüşümleri ve enrichment işlemlerini yapar.
# =============================================================================

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
import html

class ChatMessageService:
    """
    Chat mesajlarının işlenmesi ve formatlanmasını yöneten servis.
    """
    
    def __init__(self):
        """Chat message servisini başlatır."""
        # Chat repository'yi import et
        from app.database.chat_repository import ChatRepository
        self.chat_repo = ChatRepository()
        
        # Mesaj formatı kuralları
        self.format_rules = {
            'max_length': 2000,
            'min_length': 1,
            'allowed_html_tags': ['b', 'i', 'u', 'br', 'p', 'strong', 'em'],
            'forbidden_patterns': [
                r'<script.*?</script>',
                r'javascript:',
                r'on\\w+=".*?"'
            ]
        }
        
        # Quick action definitions
        self.quick_actions = {
            'explain': {
                'prompt_template': 'Bu soruyu öğrenciye basit ve anlaşılır bir şekilde açıkla: {question_text}',
                'context_hint': 'Açıklama yaparken adım adım ilerle ve örnekler ver.'
            },
            'hint': {
                'prompt_template': 'Bu soru için öğrenciye yardımcı olacak bir ipucu ver (cevabı verme): {question_text}',
                'context_hint': 'İpucu verirken doğrudan cevabı söyleme, düşünmeye yönlendir.'
            },
            'related': {
                'prompt_template': 'Bu konu ile ilgili benzer sorular ve konular öner: {topic}',
                'context_hint': 'İlgili konuları ve pratik önerilerini paylaş.'
            }
        }
    
    def validate_message(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Mesajın geçerli olup olmadığını kontrol eder.
        
        Args:
            message: Kontrol edilecek mesaj
            
        Returns:
            (is_valid, error_message)
        """
        if not message or not message.strip():
            return False, "Mesaj boş olamaz"
        
        if len(message) < self.format_rules['min_length']:
            return False, "Mesaj çok kısa"
        
        if len(message) > self.format_rules['max_length']:
            return False, f"Mesaj çok uzun (maksimum {self.format_rules['max_length']} karakter)"
        
        # Güvenlik kontrolü - zararlı pattern'ler
        for pattern in self.format_rules['forbidden_patterns']:
            if re.search(pattern, message, re.IGNORECASE):
                return False, "Mesaj güvenlik kontrolünden geçemedi"
        
        return True, None
    
    def sanitize_message(self, message: str) -> str:
        """
        Mesajı güvenli hale getirir.
        
        Args:
            message: Temizlenecek mesaj
            
        Returns:
            Temizlenmiş mesaj
        """
        # HTML escape
        sanitized = html.escape(message.strip())
        
        # İzin verilen HTML tag'leri geri al (basic formatting için)
        for tag in self.format_rules['allowed_html_tags']:
            sanitized = sanitized.replace(f'&lt;{tag}&gt;', f'<{tag}>')
            sanitized = sanitized.replace(f'&lt;/{tag}&gt;', f'</{tag}>')
        
        return sanitized
    
    def format_ai_response(self, response: str) -> str:
        """
        AI yanıtını kullanıcı dostu formata çevirir.
        
        Args:
            response: AI'dan gelen ham yanıt
            
        Returns:
            Formatlanmış yanıt
        """
        if not response:
            return "Üzgünüm, yanıt oluşturulamadı. 😔"
        
        # Temel temizlik
        formatted = response.strip()
        
        # Çok uzun yanıtları kısalt
        if len(formatted) > self.format_rules['max_length']:
            formatted = formatted[:self.format_rules['max_length'] - 3] + "..."
        
        # Markdown-style formatting'i HTML'e çevir
        formatted = self._convert_markdown_to_html(formatted)
        
        # Emoji ekleme
        formatted = self._add_contextual_emojis(formatted)
        
        return formatted
    
    def _convert_markdown_to_html(self, text: str) -> str:
        """
        Basit markdown formatını HTML'e çevirir.
        
        Args:
            text: Markdown içeren text
            
        Returns:
            HTML formatındaki text
        """
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Line breaks
        text = text.replace('\n', '<br>')
        
        return text
    
    def _add_contextual_emojis(self, text: str) -> str:
        """
        Context'e göre uygun emoji'ler ekler.
        
        Args:
            text: Emoji eklenecek text
            
        Returns:
            Emoji'li text
        """
        # Belirli kelimeler için emoji mapping
        emoji_map = {
            r'\b(doğru|correct|right)\b': '✅',
            r'\b(yanlış|wrong|incorrect)\b': '❌',
            r'\b(dikkat|attention|important)\b': '⚠️',
            r'\b(ipucu|hint|tip)\b': '💡',
            r'\b(açıklama|explanation)\b': '📚',
            r'\b(örnek|example)\b': '📝',
            r'\b(soru|question)\b': '❓',
            r'\b(cevap|answer)\b': '💬',
            r'\b(başarılı|success|great)\b': '🎉',
        }
        
        for pattern, emoji in emoji_map.items():
            if re.search(pattern, text, re.IGNORECASE):
                # Her cümlenin sonuna değil, sadece ilk bulduğumuz yere ekle
                if emoji not in text:
                    text = re.sub(pattern, f'\\g<0> {emoji}', text, count=1, flags=re.IGNORECASE)
        
        return text
    
    def create_quick_action_prompt(self, action: str, question_data: Dict[str, Any]) -> Optional[str]:
        """
        Quick action için prompt oluşturur.
        
        Args:
            action: Action tipi ('explain', 'hint', 'related')
            question_data: Soru bilgileri
            
        Returns:
            Prompt string veya None
        """
        if action not in self.quick_actions:
            return None
        
        action_config = self.quick_actions[action]
        
        # Template'i doldur
        question_text = question_data.get('question_text', '')
        topic = question_data.get('topic_name', '')
        
        prompt = action_config['prompt_template'].format(
            question_text=question_text,
            topic=topic
        )
        
        # Context hint ekle
        prompt += f"\n\n{action_config['context_hint']}"
        
        return prompt
    
    def create_message_metadata(self, message_type: str, action: Optional[str] = None, question_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Mesaj için metadata oluşturur.
        
        Args:
            message_type: Mesaj tipi
            action: Action tipi (optional)
            question_id: Soru ID (optional)
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'message_type': message_type,
            'timestamp': datetime.now().isoformat(),
            'processed_at': datetime.now().isoformat()
        }
        
        if action:
            metadata['action'] = action
        
        if question_id:
            metadata['question_id'] = question_id
        
        return metadata
    
    def get_error_message(self, error_type: str) -> str:
        """
        Hata tipi için kullanıcı dostu mesaj döndürür.
        
        Args:
            error_type: Hata tipi
            
        Returns:
            Kullanıcı dostu hata mesajı
        """
        error_messages = {
            'api_error': 'AI servisi geçici olarak kullanılamıyor. Lütfen biraz sonra tekrar deneyin. 🔄',
            'timeout': 'Yanıt süresi aşıldı. Lütfen tekrar deneyin. ⏱️',
            'validation_error': 'Mesajınızda bir sorun var. Lütfen kontrol edin. ❌',
            'session_error': 'Oturum bilgisi bulunamadı. Sayfayı yenileyin. 🔄',
            'question_error': 'Soru bilgisi alınamadı. Lütfen tekrar deneyin. ❓',
            'general_error': 'Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin. 😔'
        }
        
        return error_messages.get(error_type, error_messages['general_error'])
    
    def get_chat_history(self, chat_session_id: str) -> List[Dict[str, Any]]:
        """
        Belirli bir chat session için chat history'yi getirir
        
        Args:
            chat_session_id: Chat session ID
            
        Returns:
            Chat mesajları listesi
        """
        try:
            # Mesajları getir
            messages = self.chat_repo.get_chat_messages(chat_session_id)
            
            # Mesajları formatla
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    'id': msg['id'],
                    'role': msg['role'],  # message_type as role olarak geldi
                    'content': msg['content'],
                    'label': msg.get('label'),
                    'timestamp': msg['created_at'].isoformat() if msg['created_at'] else None
                })
            
            return formatted_messages
            
        except Exception as e:
            return []
    
    def create_system_message(self, message_type: str, context: Dict[str, Any] = None) -> str:
        """
        Sistem mesajları oluşturur.
        
        Args:
            message_type: Sistem mesajı tipi
            context: Ek context bilgileri
            
        Returns:
            Sistem mesajı
        """
        system_messages = {
            'welcome': 'Merhaba! Ben Daima, senin AI öğretmenin! Sorularınla ilgili yardıma ihtiyacın var mı? 🤖✨',
            'question_changed': 'Yeni bir soru! Bu konuda yardıma ihtiyacın var mı? 🤔',
            'session_started': 'AI sohbet başlatıldı. İyi çalışmalar! 📚',
            'session_ended': 'Sohbet sonlandırıldı. Başarılar! 👋',
            'service_available': 'AI sohbet servisi aktif! 🟢',
            'service_unavailable': 'AI sohbet servisi şu anda kullanılamıyor. 🔴'
        }
        
        base_message = system_messages.get(message_type, '')
        
        # Context bilgilerini ekle
        if context and message_type == 'question_changed':
            subject = context.get('subject', '')
            topic = context.get('topic', '')
            if subject and topic:
                base_message = f'{subject} - {topic} hakkında yeni bir soru! Yardıma ihtiyacın var mı? 🤔'
        
        return base_message