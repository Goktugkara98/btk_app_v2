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
import os
import json

class ChatMessageService:
    """
    Chat mesajlarının işlenmesi ve formatlanmasını yöneten servis.
    """
    
    def __init__(self, db_connection=None):
        """Chat message servisini başlatır."""
        # Chat repository'yi import et
        from app.database.repositories.chat_repository import ChatRepository
        self.chat_repo = ChatRepository(db_connection) if db_connection else ChatRepository()
        
        # Chat session service'i import et (prompt oluşturma için)
        try:
            from app.services.chat_session_service import ChatSessionService
            self.chat_session_service = ChatSessionService(db_connection)
        except ImportError:
            self.chat_session_service = None
        
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
        
        # AI scenarios base directory
        try:
            app_dir = os.path.dirname(os.path.dirname(__file__))  # app/
            self.scenario_base_dir = os.path.join(app_dir, 'data', 'ai_scenarios')
        except Exception:
            self.scenario_base_dir = None
        
        # Quick action template base directory (file-based per action)
        self.quick_action_template_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'data', 'ai_scenarios', 'quick_action', 'actions')
        )
        
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
        
        # JSON'dan yüklenen senaryo metinleri
        self.scenario_texts: Dict[str, Any] = {}
        
        # Scenario metinlerini yükle
        try:
            self.scenario_texts = self._load_scenarios()
        except Exception as e:
            print(f"[WARNING] Failed to load scenarios: {e}")
            self.scenario_texts = {}
    
    # =============================================================================
    # MESSAGE STORAGE
    # =============================================================================
    
    def add_message(self, chat_session_id: str, message_type: str, content: str, action_type: Optional[str] = None, 
                   ai_model: Optional[str] = None, prompt_used: Optional[str] = None, 
                   response_time_ms: Optional[int] = None, metadata: Optional[Dict] = None) -> Optional[int]:
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
                print(f"[ERROR] Failed to add message: {e}")
                return None
        return None
    
    # =============================================================================
    # SCENARIO LOADING
    # =============================================================================
    
    def _load_scenarios(self) -> Dict[str, Any]:
        """AI scenario metinlerini JSON dosyalarından yükler."""
        scenarios = {}
        
        if not self.scenario_base_dir or not os.path.exists(self.scenario_base_dir):
            return scenarios
        
        try:
            # shared.json'u yükle
            shared_path = os.path.join(self.scenario_base_dir, 'shared.json')
            if os.path.exists(shared_path):
                with open(shared_path, 'r', encoding='utf-8') as f:
                    scenarios['shared'] = json.load(f)
            
            # Diğer scenario dosyalarını yükle
            for filename in os.listdir(self.scenario_base_dir):
                if filename.endswith('.json') and filename != 'shared.json':
                    scenario_name = filename[:-5]  # .json'u çıkar
                    file_path = os.path.join(self.scenario_base_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        scenarios[scenario_name] = json.load(f)
        except Exception as e:
            print(f"[ERROR] Scenario loading failed: {e}")
        
        return scenarios
    
    def process_message_with_full_prompt(self, message_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mesaj bilgilerini işler, kullanıcı aksiyonu ile promptu birleştirir ve tam promptu döndürür.
        
        Args:
            message_info: Tüm mesaj bilgileri
            
        Returns:
            {
                'success': bool,
                'contents': List[Dict],  # Gemini API için
                'full_prompt': str,      # Tam prompt metni
                'final_user_text': str,  # Son kullanıcı mesajı
                'error': str             # Hata mesajı (varsa)
            }
        """
        try:
            if not self.chat_session_service:
                return {
                    'success': False,
                    'error': 'Chat session service not available'
                }
            
            # Debug: Question context'i logla
            print(f"[DEBUG] Question context: {message_info.get('question_context')}")
            print(f"[DEBUG] Is first message: {message_info['is_first_message']}")
            print(f"[DEBUG] Scenario type: {message_info['scenario_type']}")
            
            # Kendi prompt building metodumuzu kullan
            built = self.build_gemini_contents_for_scenario(
                chat_session_id=message_info['chat_session_id'],
                user_message=message_info['user_message'],
                scenario_type=message_info['scenario_type'],
                is_first_message=message_info['is_first_message'],
                question_context=message_info['question_context'],
                files_only=True,
            )
            
            contents = built.get('contents', [])
            final_user_text = built.get('final_user_text', '')
            
            if not contents or not str(final_user_text).strip():
                return {
                    'success': False,
                    'error': 'Scenario template not found or empty'
                }
            
            # Tam promptu oluştur (tüm contents'leri birleştir)
            full_prompt_parts = []
            for content in contents:
                role = content.get('role', 'unknown')
                parts = content.get('parts', [])
                for part in parts:
                    text = part.get('text', '')
                    if text.strip():
                        full_prompt_parts.append(f"[{role.upper()}]: {text}")
            
            full_prompt = '\n\n'.join(full_prompt_parts)
            
            # Enhanced user metadata oluştur
            user_metadata = self.create_message_metadata(
                'user',
                question_id=message_info.get('question_id'),
                scenario_type=message_info['scenario_type'],
                user_action=message_info.get('user_action', {}),
                is_first_message=message_info['is_first_message'],
                full_prompt=full_prompt
            )
            
            # Mesajı veritabanına kaydet (tam prompt ile)
            action_type = self._determine_action_type(message_info.get('user_action', {}))
            
            self.save_message_with_full_prompt(
                chat_session_id=message_info['chat_session_id'],
                role='user',
                content=message_info['user_message'],
                action_type=action_type,
                metadata=user_metadata,
                full_prompt=full_prompt
            )
            
            return {
                'success': True,
                'contents': contents,
                'full_prompt': full_prompt,
                'final_user_text': final_user_text,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Message processing failed: {str(e)}'
            }
    
    def _determine_action_type(self, user_action: Dict[str, Any]) -> str:
        """Kullanıcı aksiyonundan action type'ı belirler."""
        action_type = user_action.get('type', 'general')
        
        if action_type == 'direct_message':
            return 'direct_message'
        elif action_type == 'wrong_answer':
            return 'wrong_answer_analysis'
        elif action_type == 'quick_action':
            return 'quick_action'
        else:
            return 'general'
    
    def save_message_with_full_prompt(
        self, 
        chat_session_id: str, 
        role: str, 
        content: str,
        action_type: str = 'general',
        metadata: Optional[Dict[str, Any]] = None,
        full_prompt: Optional[str] = None
    ) -> bool:
        """
        Mesajı tam prompt ile birlikte veritabanına kaydeder.
        
        Args:
            chat_session_id: Chat session ID
            role: Mesaj rolü (user/ai)
            content: Mesaj içeriği
            action_type: Aksiyon tipi
            metadata: Metadata bilgileri
            full_prompt: Yapay zekaya gönderilen tam prompt
            
        Returns:
            bool: Kayıt başarılı mı
        """
        try:
            # Metadata'ya full prompt'u ekle
            if metadata is None:
                metadata = {}
            
            metadata['full_prompt'] = full_prompt
            metadata['timestamp'] = datetime.now().isoformat()
            
            # Chat repository üzerinden kaydet
            if self.chat_repo:
                return self.chat_repo.add_message(
                    chat_session_id=chat_session_id,
                    message_type=role,  # 'role' yerine 'message_type' kullan
                    content=content,
                    action_type=action_type,
                    metadata=metadata
                )
            
            return False
            
        except Exception as e:
            print(f"Error saving message with full prompt: {e}")
            return False
    
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
        
        # HTML etiketlerinin içinde değişiklik yapmamak için metni tag'lere göre böl
        try:
            segments = re.split(r'(<[^>]+>)', text)
        except Exception:
            segments = [text]
        
        # Metinde halihazırda bulunan emojileri dikkate alarak, her emoji'den en fazla bir tane ekle
        emoji_inserted = {e: (e in text) for e in emoji_map.values()}
        
        # Her pattern için, ilk uygun metin segmentine emojiyi ekle
        for pattern, emoji in emoji_map.items():
            if emoji_inserted.get(emoji):
                continue
            for i in range(0, len(segments), 2):  # 0,2,4... metin segmentleri (tag olmayanlar)
                seg = segments[i]
                if not seg:
                    continue
                if re.search(pattern, seg, re.IGNORECASE):
                    segments[i] = re.sub(pattern, r'\g<0> ' + emoji, seg, count=1, flags=re.IGNORECASE)
                    emoji_inserted[emoji] = True
                    break
        
        return ''.join(segments)
    
    
    def create_message_metadata(
        self, 
        message_type: str, 
        action: Optional[str] = None, 
        question_id: Optional[int] = None,
        scenario_type: Optional[str] = None,
        user_action: Optional[Dict[str, Any]] = None,
        is_first_message: Optional[bool] = None,
        full_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mesaj için gelişmiş metadata oluşturur.
        
        Args:
            message_type: Mesaj tipi
            action: Action tipi (optional)
            question_id: Soru ID (optional)
            scenario_type: Senaryo tipi (optional)
            user_action: Kullanıcı aksiyonu bilgileri (optional)
            is_first_message: İlk mesaj mı (optional)
            full_prompt: Yapay zekaya gönderilen tam prompt (optional)
            
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
            
        if scenario_type:
            metadata['scenario_type'] = scenario_type
            
        if user_action:
            metadata['user_action'] = user_action
            
        if is_first_message is not None:
            metadata['is_first_message'] = is_first_message
            
        if full_prompt:
            metadata['full_prompt'] = full_prompt
        
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
    
    # =============================================================================
    # PROMPT BUILDING METHODS (Moved from ChatSessionService)
    # =============================================================================
    
    def reload_scenarios(self) -> bool:
        """JSON senaryo konfigürasyonlarını yeniden yükler."""
        try:
            self.scenario_texts = self._load_scenarios()
            return True
        except Exception:
            return False
    
    def _get_intro_text(self) -> str:
        """JSON'dan intro metnini al, yoksa varsayılanı kullan."""
        intro = ''
        try:
            intro = (self.scenario_texts.get('shared') or {}).get('intro', '').strip()
        except Exception:
            intro = ''
        if not intro:
            intro = self.context_templates['educational_intro']
        return intro
    
    def _get_scenario_directive(self, scenario_type: str, is_first_message: bool) -> str:
        """
        Senaryoya uygun direktif metnini JSON'dan getirir. Yoksa akıllı geri dönüş sağlar.
        Beklenen anahtarlar: 'first' / 'followup' veya 'default'
        """
        scen = (self.scenario_texts.get(scenario_type) or {}) if isinstance(self.scenario_texts, dict) else {}
        text = ''
        if scen:
            key = 'first' if is_first_message else 'followup'
            # Önce nested directive yapısını dene
            try:
                dir_conf = scen.get('directive') if isinstance(scen, dict) else None
                if isinstance(dir_conf, dict):
                    text = (dir_conf.get(key) or dir_conf.get('default') or '').strip()
            except Exception:
                text = ''
            # Root seviyesinde eski anahtarları da destekle
            if not text:
                text = (scen.get(key) or scen.get('default') or '').strip()
        if text:
            return text

        # Geriye dönük uyumluluk: sabit metinlere dön
        if scenario_type == 'wrong_answer':
            return (
                "Öğrenci soruya yanlış cevap verdi. "
                "Doğrudan doğru cevabı söyleme; önce hatayı analiz et, ipucu ver, gerekirse düşünme adımlarını yönlendir."
                if is_first_message else
                "Öğrenci daha önce yanlış cevap verdi. "
                "Önceki rehberliği kısaca hatırlat ve yeni bir ipucu veya açıklama ekle."
            )
        if scenario_type == 'quick_action':
            return (
                "Bu bir hızlı eylem isteği. "
                "İstenen eyleme uygun, kısa ve net yanıt ver."
            )
        # default: direct
        return (
            "Bu, öğrencinin bu sorudaki ilk mesajı. "
            "Bağlamı hızlıca özetle ve kısa, anlaşılır bir yanıt ver."
            if is_first_message else
            "Önceki konuşmaları dikkate al. "
            "Kısa ve odaklı bir yanıt ver."
        )
    
    def _render_text(self, text: str, variables: Dict[str, Any]) -> str:
        """Placeholder'ları güvenli şekilde doldurur."""
        class _SafeDict(dict):
            def __missing__(self, key):
                return ''
        try:
            return text.format_map(_SafeDict(**variables))
        except Exception:
            return text

    def _load_file_prompt(
        self,
        scenario_type: str,
        is_first_message: bool,
        action: Optional[str] = None
    ) -> str:
        """
        Dosya tabanlı promptu yükler. Aşağıdaki yolları dener:
        - app/data/ai_scenarios/direct/first.md | followup.md
        - app/data/ai_scenarios/wrong_answer/first.md | followup.md
        - app/data/ai_scenarios/quick_action/actions/<action>/first.md | followup.md
        """
        base = self.scenario_base_dir
        if not base:
            return ''
        fname = 'first.md' if is_first_message else 'followup.md'
        scen = scenario_type.strip().lower() if scenario_type else ''
        candidates: List[str] = []
        try:
            if scen == 'quick_action':
                # quick_action requires an action subfolder
                import re as _re
                safe_action = _re.sub(r'[^a-zA-Z0-9_\-]', '', action or '')
                if not safe_action:
                    return ''
                candidates.append(os.path.join(base, 'quick_action', 'actions', safe_action, fname))
            else:
                candidates.append(os.path.join(base, scen, fname))
        except Exception:
            return ''
        for path in candidates:
            try:
                if os.path.isfile(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()
            except Exception:
                continue
        return ''
    
    def _prepare_question_vars(self, question_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Soru/şık değişkenlerini hazırlar (bulleted/plain ve doğru şık tespiti)."""
        vars_out: Dict[str, Any] = {
            'question_text': '',
            'options_bulleted': '',
            'options_plain': '',
            'correct_answer_text': '',
            'correct_option_letter': ''
        }
        if not question_context:
            return vars_out
        q_text = str(question_context.get('question_text', '') or '').strip()
        options = question_context.get('options', []) or []
        vars_out['question_text'] = q_text
        if not options:
            return vars_out
        letters = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
            'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
            'U', 'V', 'W', 'X', 'Y', 'Z'
        ]
        bulleted_lines: List[str] = []
        plain_lines: List[str] = []
        correct_text = ''
        correct_letter = ''
        for idx, opt in enumerate(options):
            letter = letters[idx] if idx < len(letters) else str(idx + 1)
            otext = str(opt.get('option_text') or opt.get('text') or '').strip()
            if not otext:
                otext = 'Şık metni bulunamadı'
            bulleted_lines.append(f"- {letter}) {otext}")
            plain_lines.append(f"{letter}) {otext}")
            is_correct = bool(opt.get('is_correct')) if 'is_correct' in opt else (str(opt.get('isCorrect')).lower() == 'true' if 'isCorrect' in opt else False)
            if is_correct and not correct_text:
                correct_text = otext
                correct_letter = letter
        vars_out['options_bulleted'] = "\n".join(bulleted_lines)
        vars_out['options_plain'] = "\n".join(plain_lines)
        vars_out['correct_answer_text'] = correct_text
        vars_out['correct_option_letter'] = correct_letter
        return vars_out
    
    def build_prompt_for_scenario(
        self,
        chat_session_id: str,
        user_message: str,
        scenario_type: str = 'direct',
        is_first_message: bool = False,
        question_context: Optional[Dict[str, Any]] = None,
        action: Optional[str] = None,
        files_only: bool = True,
    ) -> str:
        """
        Senaryoya göre (ilk mesaj/sonraki mesaj, yanlış cevap/direkt mesaj/hızlı eylem) özel prompt üretir.

        Args:
            chat_session_id: Chat session ID
            user_message: Kullanıcı mesajı veya oluşturulmuş kullanıcı bağlamı
            scenario_type: 'direct', 'wrong_answer', 'quick_action'
            is_first_message: True ise ilk mesaj senaryosu
            question_context: Soru metni ve şıkları (opsiyonel)
            action: Quick action için action tipi
            files_only: Sadece dosya bazlı şablonları kullan

        Returns:
            Senaryoya göre hazırlanmış prompt metni
        """
        # Session bilgilerini al
        session_info = self.chat_session_service.get_session(chat_session_id) if self.chat_session_service else {}
        
        # Ortak değişkenleri hazırla
        shared_conf: Dict[str, Any] = self.scenario_texts.get('shared') or {}
        context_conf: Dict[str, Any] = (shared_conf.get('context') or {}) if isinstance(shared_conf, dict) else {}
        hist_conf: Dict[str, Any] = context_conf.get('history') or {}
        q_conf: Dict[str, Any] = context_conf.get('question') or {}

        # Tarihçe artık Gemini contents'e dahil edildiği için burada boş bırak
        history_str = ""

        has_history = bool(history_str)

        # Soru bağlamını derle (konfigüre edilebilir)
        include_q = False
        if question_context:
            include_q = bool(q_conf.get('include_on_first', True)) if is_first_message else bool(q_conf.get('include_on_followup', False))
        q_block = ''
        if question_context and include_q:
            q_text = str(question_context.get('question_text', '')).strip()
            options = question_context.get('options', []) or []
            label_question = (q_conf.get('labels', {}) or {}).get('question', 'Soru')
            label_options = (q_conf.get('labels', {}) or {}).get('options', 'Şıklar')
            opt_fmt = q_conf.get('option_format', '{index}) {text}')
            lines: List[str] = []
            if q_text:
                lines.append(f"{label_question}: {q_text}")
            if options:
                lines.append(f"{label_options}:")
                for idx, opt in enumerate(options, 1):
                    otext = str(opt.get('option_text', '')).strip() or 'Şık metni bulunamadı'
                    lines.append(self._render_text(opt_fmt, {'index': idx, 'text': otext}))
            q_block = "\n".join(lines)

        # Senaryo yönergesi
        directive = self._get_scenario_directive(scenario_type, is_first_message)

        # Değişkenler
        variables = {
            'SYSTEM': self._get_intro_text(),
            'DIRECTIVE': directive,
            'USER_MESSAGE': user_message,
            'HISTORY': history_str,
            'QUESTION_BLOCK': q_block,
            'SUBJECT': session_info.get('subject_name', 'Bu ders'),
            'TOPIC': session_info.get('topic_name', 'bu konu'),
            'DIFFICULTY': session_info.get('difficulty_level', 'orta'),
        }

        # Soru/şık değişkenleri ve ek değişkenler
        variables.update(self._prepare_question_vars(question_context))
        scen_conf: Dict[str, Any] = self.scenario_texts.get(scenario_type) or {}
        try:
            extra_vars: Dict[str, Any] = {}
            if isinstance(shared_conf, dict) and isinstance(shared_conf.get('vars'), dict):
                extra_vars.update(shared_conf.get('vars'))
            if isinstance(scen_conf, dict) and isinstance(scen_conf.get('vars'), dict):
                extra_vars.update(scen_conf.get('vars'))
            variables.update(extra_vars)
        except Exception:
            pass

        # 1) DOSYA BAZLI PROMPT: Varsa sadece bunu kullan
        file_prompt = self._load_file_prompt(scenario_type, is_first_message, action=action)
        if file_prompt:
            return self._render_text(file_prompt, variables)
        if files_only:
            # Dosya yoksa ve sadece dosyalar etkinse boş dön
            return ''

        # 2) Fallback: Basit prompt oluştur
        prompt_parts = []
        if is_first_message:
            prompt_parts.append(self._get_intro_text())
        if history_str:
            prompt_parts.append("Son sohbet:\n" + history_str)
        if q_block:
            prompt_parts.append(q_block)
        prompt_parts.append(directive)
        prompt_parts.append(f"Öğrenci mesajı: {user_message}")

        return "\n\n".join(prompt_parts)
    
    def _get_recent_dialog(
        self,
        chat_session_id: str,
        last_n: int = 2,
        truncate_chars: int = 200,
        label_user: str = 'Kullanıcı',
        label_ai: str = 'AI',
    ) -> str:
        """
        Sistem mesajlarını hariç tutarak son user/ai mesajlarını formatlar.
        """
        if not self.chat_repo:
            return ''
        try:
            recent_messages = self.chat_repo.get_conversation_history(chat_session_id, limit=max(2*last_n, 6))
        except Exception:
            return ''
        if not recent_messages:
            return ''
        non_system = [m for m in recent_messages if m.get('role') in ('user', 'ai')]
        if not non_system:
            return ''
        last_dialog = non_system[-last_n:]
        lines: List[str] = []
        for msg in last_dialog:
            content = msg.get('content', '')
            if truncate_chars and len(content) > truncate_chars:
                content = content[:truncate_chars] + '...'
            role_label = label_user if msg.get('role') == 'user' else label_ai
            lines.append(f"{role_label}: {content}")
        return "\n".join(lines)
    
    def build_gemini_contents_for_scenario(
        self,
        chat_session_id: str,
        user_message: str,
        scenario_type: str = 'direct',
        is_first_message: bool = False,
        question_context: Optional[Dict[str, Any]] = None,
        action: Optional[str] = None,
        files_only: bool = True,
        history_limit: int = 12,
    ) -> Dict[str, Any]:
        """
        Gemini REST API'ye uygun 'contents' yapısını döndürür.
        - Geçmiş: veritabanından user/model mesajları (system hariç)
        - Şablon: senaryoya göre markdown dosyasını değişkenlerle doldurur
        - Son içerik: render edilen şablonu 'user' mesajı olarak ekler

        Returns:
            {
              'contents': [ {role, parts:[{text}]}... ],
              'final_user_text': str
            }
        """
        # Prompt'u oluştur
        prompt_text = self.build_prompt_for_scenario(
            chat_session_id=chat_session_id,
            user_message=user_message,
            scenario_type=scenario_type,
            is_first_message=is_first_message,
            question_context=question_context,
            action=action,
            files_only=files_only
        )
        
        if not prompt_text.strip():
            return {'contents': [], 'final_user_text': ''}
        
        # Geçmiş mesajları al (sadece user/model)
        contents = []
        if self.chat_repo:
            try:
                history = self.chat_repo.get_conversation_history(chat_session_id, limit=history_limit)
                for msg in history:
                    role = msg.get('role')
                    if role in ('user', 'ai'):
                        gemini_role = 'user' if role == 'user' else 'model'
                        content = msg.get('content', '')
                        if content.strip():
                            contents.append({
                                'role': gemini_role,
                                'parts': [{'text': content}]
                            })
            except Exception:
                pass
        
        # Son kullanıcı mesajını ekle
        contents.append({
            'role': 'user',
            'parts': [{'text': prompt_text}]
        })
        
        return {
            'contents': contents,
            'final_user_text': prompt_text
        }