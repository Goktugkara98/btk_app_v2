# =============================================================================
# CHAT SESSION SERVICE
# =============================================================================
# Bu modül, AI sohbet oturumlarını yönetir.
# Session state, context ve conversation history'yi takip eder.
# =============================================================================

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

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

        # Senaryo metinleri dizini (app/data/ai_scenarios)
        # Bu dizin altında her senaryo için bir klasör ve içinde config.json beklenir
        # Örn: app/data/ai_scenarios/direct/config.json
        try:
            app_dir = os.path.dirname(os.path.dirname(__file__))  # app/
            self.scenario_base_dir = os.path.join(app_dir, 'data', 'ai_scenarios')
        except Exception:
            self.scenario_base_dir = None

        # JSON'dan yüklenen senaryo metinleri
        self.scenario_texts: Dict[str, Any] = self._load_scenarios()
    
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
        Son konuşma geçmişini ve bağlamı döndürür.
        
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
            # Biraz daha geniş alıp (örn. 6) sadece user/ai mesajlarını filtreleyelim
            recent_messages = self.chat_repo.get_conversation_history(chat_session_id, limit=6)
            if recent_messages:
                # Sistem mesajlarını çıkar, sadece kullanıcı ve AI mesajlarını tut
                non_system = [m for m in recent_messages if m.get('role') in ('user', 'ai')]
                last_dialog = non_system[-2:] if len(non_system) > 0 else []
                if last_dialog:
                    context_parts.append("\nSon sohbet:")
                    for msg in last_dialog:
                        # Mesaj içeriğini kısalt (maksimum 200 karakter)
                        content = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
                        role_label = 'Kullanıcı' if msg.get('role') == 'user' else 'AI'
                        context_parts.append(f"{role_label}: {content}")
        
        return "\n\n".join(context_parts)

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

    def _eval_when(self, when: str, env: Dict[str, Any]) -> bool:
        """Basit koşulları değerlendirir: always, first, followup, has_history, question_allowed"""
        if not when:
            return True
        when = str(when).strip().lower()
        if when in ('always', 'true'):
            return True
        if when == 'first':
            return bool(env.get('is_first_message'))
        if when == 'followup':
            return not bool(env.get('is_first_message'))
        if when == 'has_history':
            return bool(env.get('has_history'))
        if when == 'question_allowed':
            return bool(env.get('question_allowed'))
        # bilinmeyen durumda devre dışı
        return False

    def _render_text(self, text: str, variables: Dict[str, Any]) -> str:
        """Placeholder'ları güvenli şekilde doldurur."""
        class _SafeDict(dict):
            def __missing__(self, key):
                return ''
        try:
            return text.format_map(_SafeDict(**variables))
        except Exception:
            return text

    def _read_include(self, include: str, scenario_type: Optional[str] = None) -> str:
        """
        JSON bloklarında 'include' alanıyla belirtilen dosyayı okur.
        Arama sırası:
        - app/data/ai_scenarios/<scenario_type>/<include>
        - app/data/ai_scenarios/<include>
        """
        base = self.scenario_base_dir
        if not include or not base:
            return ''
        candidates: List[str] = []
        if scenario_type:
            candidates.append(os.path.join(base, scenario_type, include))
        candidates.append(os.path.join(base, include.lstrip('/\\')))
        for path in candidates:
            try:
                if os.path.isfile(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()
            except Exception:
                continue
        return ''

    # ---------------------------------------------------------------------
    # Dosya Bazlı Prompt Yükleyici (Yeni Aktif Yapı)
    # ---------------------------------------------------------------------
    def _load_file_prompt(self, scenario_type: str, is_first_message: bool, action: Optional[str] = None) -> str:
        """
        Senaryoya göre first/followup markdown dosyasını okur.
        Yapı:
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

    # ---------------------------------------------------------------------
    # Senaryo JSON Yükleyici
    # ---------------------------------------------------------------------
    def _load_scenarios(self) -> Dict[str, Any]:
        """
        app/data/ai_scenarios dizininden senaryo metinlerini yükler.
        Beklenen yapı:
        - app/data/ai_scenarios/shared.json               -> { "intro": "..." }
        - app/data/ai_scenarios/<scenario>/config.json    -> { "first": "...", "followup": "..." | "default": "..." }
        """
        scenarios: Dict[str, Any] = { 'shared': {} }
        base = self.scenario_base_dir
        if not base or not os.path.isdir(base):
            return scenarios
        # shared
        shared_path = os.path.join(base, 'shared.json')
        try:
            if os.path.isfile(shared_path):
                with open(shared_path, 'r', encoding='utf-8') as f:
                    scenarios['shared'] = json.load(f) or {}
        except Exception:
            scenarios['shared'] = {}
        # scenario folders
        try:
            for name in os.listdir(base):
                scen_dir = os.path.join(base, name)
                if not os.path.isdir(scen_dir):
                    continue
                config_path = os.path.join(scen_dir, 'config.json')
                if os.path.isfile(config_path):
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            scenarios[name] = json.load(f) or {}
                    except Exception:
                        scenarios[name] = {}
        except Exception:
            pass
        return scenarios

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

    def build_prompt_scenario(
        self,
        chat_session_id: str,
        user_message: str,
        scenario_type: str = 'direct',
        is_first_message: bool = False,
        question_context: Optional[Dict[str, Any]] = None,
        action: Optional[str] = None,
        files_only: bool = False,
    ) -> str:
        """
        Senaryoya göre (ilk mesaj/sonraki mesaj, yanlış cevap/direkt mesaj/hızlı eylem) özel prompt üretir.

        Args:
            chat_session_id: Chat session ID
            user_message: Kullanıcı mesajı veya oluşturulmuş kullanıcı bağlamı
            scenario_type: 'direct', 'wrong_answer', 'quick_action'
            is_first_message: True ise ilk mesaj senaryosu
            question_context: Soru metni ve şıkları (opsiyonel)

        Returns:
            Senaryoya göre hazırlanmış prompt metni
        """
        # Önce ortak değişkenleri hazırla
        shared_conf: Dict[str, Any] = self.scenario_texts.get('shared') or {}
        context_conf: Dict[str, Any] = (shared_conf.get('context') or {}) if isinstance(shared_conf, dict) else {}
        hist_conf: Dict[str, Any] = context_conf.get('history') or {}
        q_conf: Dict[str, Any] = context_conf.get('question') or {}

        # Tarihçe (her istekte; sistem mesajlarını hariç tut)
        history_str = self._get_recent_dialog(
            chat_session_id,
            last_n=int(hist_conf.get('last_n', 2) or 2),
            truncate_chars=int(hist_conf.get('truncate_chars', 200) or 200),
            label_user=str(hist_conf.get('label_user', 'Kullanıcı')),
            label_ai=str(hist_conf.get('label_ai', 'AI')),
        )

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

        # Senaryo yönergesi (JSON geri dönüş için hazır tut)
        directive = self._get_scenario_directive(scenario_type, is_first_message)

        # Değişkenler
        session = self.get_session(chat_session_id) or {}
        variables = {
            'SYSTEM': self._get_intro_text(),
            'DIRECTIVE': directive,
            'USER_MESSAGE': user_message,
            'HISTORY': history_str,
            'QUESTION_BLOCK': q_block,
            'SUBJECT': session.get('subject_name', 'Bu ders'),
            'TOPIC': session.get('topic_name', 'bu konu'),
            'DIFFICULTY': session.get('difficulty_level', 'orta'),
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

        # 2) JSON destekli modüler derleme (geri dönüş)
        shared_blocks: List[Dict[str, Any]] = (shared_conf.get('blocks') or []) if isinstance(shared_conf, dict) else []
        scen_blocks_pre = (scen_conf.get('blocks_prepend') or []) if isinstance(scen_conf, dict) else []
        scen_blocks = (scen_conf.get('blocks') or []) if isinstance(scen_conf, dict) else []
        scen_blocks_post = (scen_conf.get('blocks_append') or []) if isinstance(scen_conf, dict) else []

        all_blocks: List[Dict[str, Any]] = []
        all_blocks.extend(scen_blocks_pre)
        all_blocks.extend(shared_blocks)
        all_blocks.extend(scen_blocks)
        all_blocks.extend(scen_blocks_post)

        env = {
            'is_first_message': is_first_message,
            'has_history': has_history,
            'question_allowed': bool(q_block),
            'scenario': scenario_type,
        }

        rendered_parts: List[str] = []
        for blk in sorted(all_blocks, key=lambda b: int(b.get('priority', 50))):
            if blk.get('scenarios') and scenario_type not in blk.get('scenarios'):
                continue
            when = blk.get('when', 'always')
            if not self._eval_when(when, env):
                continue
            text = str(blk.get('text', '')).strip()
            if not text and blk.get('include'):
                text = self._read_include(str(blk.get('include')), scenario_type).strip()
            if not text:
                continue
            rendered = self._render_text(text, variables)
            try:
                max_chars = int(blk.get('max_chars')) if blk.get('max_chars') is not None else None
            except Exception:
                max_chars = None
            if max_chars and len(rendered) > max_chars:
                rendered = rendered[:max_chars] + '...'
            rendered_parts.append(rendered)

        # Her ihtimale karşı ana direktif ve kullanıcı mesajını sona ekle (bloklarla gelmediyse)
        # Kuyruğa direktif ve kullanıcı mesajını ekleme davranışı konfigüre edilebilir
        append_tail = bool(scen_conf.get('append_tail', shared_conf.get('append_tail', True))) if isinstance(scen_conf, dict) or isinstance(shared_conf, dict) else True
        tail = [directive, f"Öğrenci mesajı: {user_message}"] if append_tail else []
        prompt_parts = [p for p in rendered_parts if p]
        if not prompt_parts:
            # Fallback: eski davranışa yakın birleştirme
            if is_first_message:
                prompt_parts.append(self._get_intro_text())
            if history_str:
                prompt_parts.append("Son sohbet:\n" + history_str)
            if q_block:
                prompt_parts.append(q_block)
        prompt_parts.extend(tail)

        return "\n\n".join(prompt_parts)
    
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

    # ---------------------------------------------------------------------
    # Gemini REST Contents Builder
    # ---------------------------------------------------------------------
    def build_gemini_contents_scenario(
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
        # 1) Mevcut yapıdaki değişkenleri hazırla (HISTORY'yi metin olarak da doldur)
        shared_conf: Dict[str, Any] = self.scenario_texts.get('shared') or {}
        context_conf: Dict[str, Any] = (shared_conf.get('context') or {}) if isinstance(shared_conf, dict) else {}
        hist_conf: Dict[str, Any] = context_conf.get('history') or {}
        q_conf: Dict[str, Any] = context_conf.get('question') or {}

        # Metinsel tarihçe (şablonlar için). Sistem mesajlarını hariç tut.
        history_str = self._get_recent_dialog(
            chat_session_id,
            last_n=int(hist_conf.get('last_n', 2) or 2),
            truncate_chars=int(hist_conf.get('truncate_chars', 200) or 200),
            label_user=str(hist_conf.get('label_user', 'Kullanıcı')),
            label_ai=str(hist_conf.get('label_ai', 'AI')),
        )

        # Soru bloğu
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

        directive = self._get_scenario_directive(scenario_type, is_first_message)
        session = self.get_session(chat_session_id) or {}
        variables = {
            'SYSTEM': self._get_intro_text(),
            'DIRECTIVE': directive,
            'USER_MESSAGE': user_message,
            'HISTORY': history_str,  # Yapısal geçmiş ayrı gönderilecek olsa da şablon uyumu için metinsel tarihçe
            'QUESTION_BLOCK': q_block,
            'SUBJECT': session.get('subject_name', 'Bu ders'),
            'TOPIC': session.get('topic_name', 'bu konu'),
            'DIFFICULTY': session.get('difficulty_level', 'orta'),
        }
        # Soru/şık ek değişkenleri ve paylaşılan/ senaryo özel vars
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

        # 2) Dosya şablonunu yükle ve render et
        file_prompt = self._load_file_prompt(scenario_type, is_first_message, action=action)
        final_user_text = self._render_text(file_prompt, variables) if file_prompt else ''
        if files_only and not final_user_text:
            return {'contents': [], 'final_user_text': ''}
        if not final_user_text:
            # Fallback: build_prompt_scenario ile oluştur
            final_user_text = self.build_prompt_scenario(
                chat_session_id=chat_session_id,
                user_message=user_message,
                scenario_type=scenario_type,
                is_first_message=is_first_message,
                question_context=question_context,
                action=action,
                files_only=False,
            )

        # 3) Geçmişi REST formatında topla (system hariç)
        contents: List[Dict[str, Any]] = []
        try:
            if self.chat_repo:
                raw_hist = self.chat_repo.get_conversation_history(chat_session_id, limit=history_limit)
                for msg in raw_hist:
                    role = msg.get('role')
                    if role not in ('user', 'ai'):
                        continue
                    mapped_role = 'user' if role == 'user' else 'model'
                    text = str(msg.get('content') or '')
                    if not text:
                        continue
                    contents.append({
                        'role': mapped_role,
                        'parts': [{'text': text}]
                    })
        except Exception:
            pass

        # 4) Şu anki isteğin render edilmiş içeriğini son 'user' olarak ekle
        contents.append({
            'role': 'user',
            'parts': [{'text': final_user_text}]
        })

        return {
            'contents': contents,
            'final_user_text': final_user_text
        }
    
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