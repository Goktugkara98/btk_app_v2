/**
 * =============================================================================
 * AIChatManager – AI Sohbet Yöneticisi | AI Chat Manager
 * =============================================================================
 * Eğitim modunda AI sohbet arayüzünü ve etkileşim akışını yönetir.
 *
 * İÇİNDEKİLER | TABLE OF CONTENTS
 * 1) Kurulum ve Başlatma | Setup & Initialization
 *    - constructor() - Servisleri ve UI referanslarını kurar; initialize() çağırır.
 *    - initialize() - Dinleyicileri kurar, chat'i devre dışı başlatır; servis durumu ve oturumu hazırlar.
 *    - setupMainEventListeners() - Quiz ve soru olaylarına abone olur (load/render/wrong answer).
 *    - setupEventListeners() - Giriş alanı, gönder butonu ve klavye dinleyicilerini bağlar.
 *    - setupQuickActions() - Hızlı eylem butonlarını bağlar ve işleyicileri tanımlar.
 * 2) Oturum ve Soru Bağlamı | Session & Question Context
 *    - onQuizLoaded() - İlk soru kimliğini state'ten alır ve hazırlar.
 *    - onQuestionRendered(data) - Soru değişimini işler; currentQuestionId'yi günceller ve chat'i senkronlar.
 *    - checkAndLoadChatSession() - Mevcut soru için chat geçmişini yükler ve UI'ı günceller.
 *    - getSessionId() - sessionId'yi window veya StateManager'dan elde eder.
 *    - initializeChatSession() - Soru bağlamıyla chat oturumunu başlatır.
 *    - getContextFromState(key) - State'ten gereken bağlam bilgisini döndürür.
 * 3) Servis Durumu | Service Status
 *    - checkAIServiceStatus() - Servis sağlığını kontrol eder; chat'i etkin/devre dışı yapar.
 *    - enableChat() - Giriş ve butonları etkinleştirir.
 *    - disableChat() - Giriş ve butonları devre dışı bırakır.
 *    - showServiceUnavailableMessage() - Servis kullanılamaz uyarısını gösterir.
 *    - hideServiceUnavailableMessage() - Servis uyarısını gizler.
 * 4) Chat Etkileşimleri | Chat Interactions
 *    - onIncorrectAnswer(data) - Eski olay; yanlış cevapta AI'dan analiz ister.
 *    - onWrongAnswer(data) - Otomatik analiz; anti-spam ve ilk etkileşim kontrolleriyle mesaj gönderir.
 *    - sendMessage() - Kullanıcı mesajını gönderir, AI yanıtını alıp UI'a ekler.
 *    - handleQuickAction(action) - Seçilen hızlı eylemi mesaj olarak işler/gönderir.
 * 5) Yardımcılar | Helpers
 *    - showWelcomeMessage() - Hoş geldin mesajını gösterir.
 *    - addMessage(role, text, label) - Mesajı sohbet arayüzüne ekler.
 *    - typewriterEffect(element, text, speed) - Yazı makinesi efekti uygular.
 *    - showTyping() - "Yazıyor" göstergesini gösterir.
 *    - hideTyping() - "Yazıyor" göstergesini gizler.
 *    - formatMessage(message) - Mesaj metnini güvenli/biçimli hale getirir.
 *    - autoResizeTextarea() - Girdi alanının yüksekliğini otomatik ayarlar.
 *    - clearChat() - Sohbet mesajlarını temizler.
 *    - scrollToBottom() - Mesajlar sonuna kaydırır.
 *    - debugPendingRequests() - Bekleyen istekleri günlükler.
 * 6) Dışa Aktarım | Export
 * =============================================================================
 */
class AIChatManager {
  /* =========================================================================
   * 1) Kurulum ve Başlatma | Setup & Initialization
   * ========================================================================= */
    constructor(eventBus, aiChatService) {
        this.eventBus = eventBus;
        this.aiChatService = aiChatService;
        this.currentQuestionId = null;
        this.sessionId = null;
        
        // Pending request tracking için yeni özellikler
        this.pendingRequests = new Map(); // questionId -> requestId mapping
        this.requestCounter = 0; // Unique request ID'ler için
        
        // İlk mesaj takibi için yeni özellikler
        this.firstMessageSent = new Set(); // DEPRECATED: geriye dönük uyumluluk için tutuluyor
        this.firstInteractionSent = new Set(); // Her soru için ilk etkileşim (kullanıcı veya hızlı eylem)
        this.firstUserMessageSent = new Set(); // Her soru için ilk kullanıcı mesajı gönderildi mi
        
        // Aşırı mesajı engellemek için ek kontrol yapıları
        this.cooldowns = new Map(); // questionId -> lastSentTimestamp
        this.COOLDOWN_MS = 4000; // aynı soru için 4 sn cooldown
        this.lastMessageByQuestion = new Map(); // questionId -> lastMessageText
        
        // UI elementleri
        this.chatContainer = document.getElementById('ai-chat-container');
        this.messagesContainer = document.getElementById('ai-chat-messages');
        this.inputField = document.getElementById('ai-chat-input');
        this.sendButton = document.getElementById('ai-send-button');
        this.quickActionButtons = document.querySelectorAll('.quick-action-btn');
        
        this.initialize();
    }

    /**
     * AI Chat Manager'ı başlatır
     */
    initialize() {
        this.setupEventListeners();
        this.setupQuickActions();
        
        // Başlangıçta chat'i disable et
        this.disableChat();
        
        // AI service status kontrol et
        this.checkAIServiceStatus();
        
        // Session ID'yi al
        this.getSessionId();
        
        // Ana event listener'ları ayarla
        this.setupMainEventListeners();
    }
    
    /**
     * setupMainEventListeners - Ana event listener'ları ayarlar
     */
    setupMainEventListeners() {
        
        // Quiz yüklendiğinde
        this.eventBus.subscribe('quiz:questionsLoaded', () => {
            this.onQuizLoaded();
        });
        
        // Soru render edildiğinde (her soru değişikliğinde)
        this.eventBus.subscribe('question:rendered', (data) => {
            this.onQuestionRendered(data);
        });
        
        // Yanlış cevap verildiğinde (yeni event)
        this.eventBus.subscribe('answer:wrong', (data) => {
            this.onWrongAnswer(data);
        });
    }
    
  /* =========================================================================
   * 2) Oturum ve Soru Bağlamı | Session & Question Context
   * ========================================================================= */

    /**
     * onQuizLoaded - Quiz yüklendiğinde çağrılır
     */
    onQuizLoaded() {
        
        // İlk soru ID'sini al
        if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            
            if (state && state.questions && state.questions.length > 0) {
                const idx = (typeof state.currentQuestionIndex === 'number' && state.currentQuestionIndex >= 0)
                  ? state.currentQuestionIndex
                  : 0;
                const cq = state.questions[idx];
                if (cq && cq.question && cq.question.id != null) {
                    this.currentQuestionId = cq.question.id;
                }
            }
        }
    }
    
    /**
     * onQuestionRendered - Soru render edildiğinde çağrılır (her soru değişikliğinde)
     */
    async onQuestionRendered(data) {
        
        // StateManager'dan current question ID'yi al
        let newQuestionId = null;
        if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            
            if (state && state.questions && state.questions.length > 0) {
                const idx = (typeof state.currentQuestionIndex === 'number' && state.currentQuestionIndex >= 0)
                  ? state.currentQuestionIndex
                  : 0;
                const cq = state.questions[idx];
                if (cq && cq.question && cq.question.id != null) {
                    newQuestionId = cq.question.id;
                }
            }
        }
        
        // Eğer StateManager'dan alamadıysak, event data'dan al
        if (!newQuestionId) {
            newQuestionId = data.questionId || data.question?.id || data.id;
        }
        
        // Eğer aynı soru için tekrar çağrılıyorsa, işlem yapma
        if (this.currentQuestionId === newQuestionId) {
            return;
        }
        
        // DÜZELTME: Önceki soru için TÜM bekleyen request'leri ve controller'ları temizle
        if (this.currentQuestionId) {
            // Pending request'leri temizle
            this.pendingRequests.delete(this.currentQuestionId);
            
            // Message controller'ları iptal et ve temizle
            const messageController = this.aiChatService.messageControllers.get(this.currentQuestionId);
            if (messageController) {
                messageController.abort();
                this.aiChatService.messageControllers.delete(this.currentQuestionId);
            }
            
            // Quick action controller'ları iptal et ve temizle
            const quickActionController = this.aiChatService.quickActionControllers.get(this.currentQuestionId);
            if (quickActionController) {
                quickActionController.abort();
                this.aiChatService.quickActionControllers.delete(this.currentQuestionId);
            }
        }
        
        // Chat session'ı yeni soru için sıfırla
        this.aiChatService.endChatSession();
        
        // Yeni soru ID'sini güncelle
        this.currentQuestionId = newQuestionId;
        
        // Bu soru için chat session'ı kontrol et ve gerekirse yükle
        await this.checkAndLoadChatSession();
    }
    
    /**
     * checkAndLoadChatSession - Bu soru için chat session'ı kontrol eder ve gerekirse yükler
     */
    async checkAndLoadChatSession() {
        
        if (!this.sessionId || !this.currentQuestionId) {
            console.warn('[AIChatManager] Cannot check chat session - missing sessionId or questionId');
            return;
        }
        
        try {
            // Bu soru için chat history'yi kontrol et
            const response = await this.aiChatService.getChatHistory(this.currentQuestionId);
            
            if (response.success && response.messages && response.messages.length > 0) {

                // Chat'i temizle
                this.clearChat();

                // Sadece kullanıcı/AI mesajlarını UI'da göster (system mesajlarını gizle)
                const filtered = response.messages.filter(m => m.role === 'user' || m.role === 'ai');
                filtered.forEach(msg => {
                    this.addMessage(msg.role, msg.content, msg.label, true); // isFromHistory = true
                });
                if (filtered.length === 0) {
                    // Yalnızca system mesajları varsa hoş geldin mesajını göster
                    this.showWelcomeMessage();
                }

                // Bayrakları güncelle
                const hasUser = filtered.some(m => m.role === 'user');
                const hasAI = filtered.some(m => m.role === 'ai');
                if (hasUser || hasAI) this.firstInteractionSent.add(this.currentQuestionId);
                if (hasUser) {
                    this.firstUserMessageSent.add(this.currentQuestionId);
                    // Geriye dönük uyumluluk için
                    this.firstMessageSent.add(this.currentQuestionId);
                }

            } else {
                
                // Chat'i temizle
                this.clearChat();
                
                // Bu soru için ilk mesaj gönderilmemiş olarak işaretle
                this.firstMessageSent.delete(this.currentQuestionId);
                this.firstInteractionSent.delete(this.currentQuestionId);
                this.firstUserMessageSent.delete(this.currentQuestionId);
                
                // Karşılama mesajını göster
                this.showWelcomeMessage();
            }
        } catch (error) {
            console.error('[AIChatManager] Error checking chat session:', error);
            
            // Hata durumunda chat'i temizle ve welcome message göster
            this.clearChat();
            this.showWelcomeMessage();
        }
    }
    
  /* =========================================================================
   * 4) Chat Etkileşimleri | Chat Interactions
   * ========================================================================= */

    /**
     * onIncorrectAnswer - Yanlış cevap verildiğinde çağrılır (eski event)
     */
    async onIncorrectAnswer(data) {
        
        // Chat session'ı başlat (eğer başlatılmamışsa)
        await this.initializeChatSession();
        
        // Yanlış cevap bilgisini AI'ya gönder
        // Kullanıcı ve doğru cevap ID'lerini seçenek metinlerine çevir
        let userAnswerText = data.userAnswer;
        let correctAnswerText = data.correctAnswer?.id || data.correctAnswer;
        try {
            const qData = this.aiChatService?.getCurrentQuestionData?.();
            const options = qData?.options || [];
            const userOpt = options.find(o => String(o.id) === String(data.userAnswer));
            if (userOpt) userAnswerText = userOpt.option_text;
            const correctId = (data.correctAnswer && typeof data.correctAnswer === 'object') ? data.correctAnswer.id : data.correctAnswer;
            const correctOpt = options.find(o => String(o.id) === String(correctId));
            if (correctOpt) correctAnswerText = correctOpt.option_text;
        } catch (e) {
            console.warn('[AIChatManager] Could not map answer IDs to texts (incorrect):', e);
        }
        const message = `Yanlış cevap verdim. Seçtiğim cevap: ${userAnswerText}. Doğru cevap: ${correctAnswerText}. Lütfen yardım et.`;
        
        try {
            // AI'dan yanıt al (legacy incorrect handler)
            const qIdLegacy = data.questionId || this.currentQuestionId;
            const isFirstForInteractionLegacy = !this.firstInteractionSent.has(qIdLegacy);
            const response = await this.aiChatService.sendChatMessage(
                message,
                this.currentQuestionId,
                isFirstForInteractionLegacy,
                'wrong_answer'
            );
            
            if (response.success) {
                this.addMessage('ai', response.message);
            } else {
                this.addMessage('system', `Üzgünüm, bir hata oluştu: ${response.error || 'Bilinmeyen hata'}`);
            }
        } catch (error) {
            console.error('[AIChatManager] Error in incorrect answer handling:', error);
            this.addMessage('system', 'Yanlış cevap analizi sırasında hata oluştu.');
        }
    }

    /**
     * onWrongAnswer - Yanlış cevap verildiğinde tetiklenen otomatik analiz.
     * @param {Object} data
     * @param {string|number} data.questionId
     * @param {string|number} data.userAnswer
     * @param {string|number|Object} data.correctAnswer
     */
    async onWrongAnswer(data) {
        
        // Chat session'ı başlat (eğer başlatılmamışsa)
        await this.initializeChatSession();
        
        // Yanlış cevap bilgisini AI'ya gönder - ID'leri metinlere çevir
        let userAnswerText2 = data.userAnswer;
        let correctAnswerText2 = data.correctAnswer?.id || data.correctAnswer;
        try {
            const qData = this.aiChatService?.getCurrentQuestionData?.();
            const options = qData?.options || [];
            const userOpt = options.find(o => String(o.id) === String(data.userAnswer));
            if (userOpt) userAnswerText2 = userOpt.option_text;
            const correctId = (data.correctAnswer && typeof data.correctAnswer === 'object') ? data.correctAnswer.id : data.correctAnswer;
            const correctOpt = options.find(o => String(o.id) === String(correctId));
            if (correctOpt) correctAnswerText2 = correctOpt.option_text;
        } catch (e) {
            console.warn('[AIChatManager] Could not map answer IDs to texts (wrong):', e);
        }
        const message = `Yanlış cevap verdim. Seçtiğim cevap: ${userAnswerText2}. Doğru cevap: ${correctAnswerText2}. Lütfen yardım et.`;

        // Anti-spam: aynı soru için birden fazla otomatik analiz gönderimini engelle
        const qId = data.questionId || this.currentQuestionId;
        if (!qId) {
            console.warn('[AIChatManager] Missing questionId for wrong answer event');
            return;
        }
        // Eğer bu soru için zaten ilk etkileşim gönderildiyse, tekrar otomatik gönderme
        // (Bu kontrol yanlış cevap analizini engelliyor - kaldırıldı)
        // if (this.firstInteractionSent.has(qId)) {
        //     console.warn('[AIChatManager] Skipping auto-analysis: already sent for question', qId);
        //     return;
        // }
        // Cooldown kontrolü
        const now = Date.now();
        const lastSent = this.cooldowns.get(qId) || 0;
        if (now - lastSent < this.COOLDOWN_MS) {
            console.warn('[AIChatManager] Skipping due to cooldown for question', qId);
            return;
        }
        // Aynı içeriği üst üste göndermeyi engelle (sadece direct mesajlar için)
        const lastMsg = this.lastMessageByQuestion.get(qId);
        if (lastMsg && lastMsg === message && !message.includes('yanlış cevap verdi')) {
            console.warn('[AIChatManager] Skipping duplicate message for question', qId);
            return;
        }
        // Aynı soru için bekleyen istek varsa yeni istek başlatma
        if (this.pendingRequests.has(qId)) {
            console.warn('[AIChatManager] Skipping: request already pending for question', qId);
            return;
        }
        this.pendingRequests.set(qId, ++this.requestCounter);
        this.lastMessageByQuestion.set(qId, message);
        
        // AI status'u "Düşünüyor..." olarak güncelle
        this.updateAIStatus('thinking', 'Düşünüyor...');
        
        // Loading durumu göster
        this.showTyping();
        
        try {
            // AI'ya mesaj gönder
            // İlk etkileşimde soru bağlamını (question_context) ekle
            const isFirstForInteraction = !this.firstInteractionSent.has(qId);
            
            // Mesaj verisi paketini hazırla
            const messageData = {
                message: message,
                questionId: this.currentQuestionId,
                isFirstMessage: isFirstForInteraction,
                scenarioType: 'wrong_answer',
                questionContext: this.aiChatService.getCurrentQuestionData(),
                userAction: {
                    type: 'wrong_answer',
                    trigger: 'auto_trigger',
                    context: {
                        selectedAnswer: userAnswerText2,
                        correctAnswer: correctAnswerText2,
                        timestamp: now
                    }
                }
            };
            
            const response = await this.aiChatService.sendChatMessage(messageData);
            
            if (response.success) {
                // AI yanıtını chat'e ekle
                this.addMessage('ai', response.message || 'Yanlış cevabınızı analiz ediyorum...');
                // Bu soru için ilk etkileşimi gönderilmiş say ve cooldown başlat
                this.firstInteractionSent.add(qId);
                this.cooldowns.set(qId, Date.now());
            } else {
                console.error('[AIChatManager] Failed to send wrong answer message:', response.error);
                this.addMessage('error', 'Yanlış cevap analizi başlatılamadı.');
            }
            
            // Typing durumunu gizle
            this.hideTyping();
        } catch (error) {
            console.error('[AIChatManager] Error sending wrong answer message:', error);
            this.addMessage('error', 'Yanlış cevap bilgisi gönderilirken bir hata oluştu.');
            this.hideTyping();
        } finally {
            // Pending state'i temizle
            this.pendingRequests.delete(qId);
        }
    }
    
    /**
     * getSessionId - Session ID'yi window veya StateManager'dan alır
     */
    getSessionId() {
        
        // Önce window.QUIZ_CONFIG'den dene
        if (window.QUIZ_CONFIG && window.QUIZ_CONFIG.sessionId) {
            this.sessionId = window.QUIZ_CONFIG.sessionId;
            return;
        }
        
        // StateManager'dan dene
        if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            if (state && state.sessionId) {
                this.sessionId = state.sessionId;
                return;
            }
        }
        
        console.warn('[AIChatManager] Session ID not found');
    }
    
    /**
     * initializeChatSession - Chat session'ını başlatır
     */
    async initializeChatSession() {
        
        if (!this.sessionId || !this.currentQuestionId || !this.aiChatService.isServiceEnabled()) {
            console.warn('[AIChatManager] Cannot initialize chat session - missing sessionId, questionId or service disabled');
            return;
        }

        try {
            // Quiz context bilgilerini al
            const context = {
                subject: this.getContextFromState('subject') || 'Türkçe',
                topic: this.getContextFromState('topic') || 'Sıfat-fiil',
                difficulty: this.getContextFromState('difficulty') || 'kolay'
            };

            const result = await this.aiChatService.startChatSession(this.sessionId, this.currentQuestionId, context);
            
            if (result.success) {
                this.enableChat();
            } else {
                this.disableChat();
                console.error('[AIChatManager] Failed to initialize chat session:', result.error);
            }
        } catch (error) {
            this.disableChat();
            console.error('[AIChatManager] Chat session initialization error:', error);
        }
    }

    /**
     * getContextFromState - State'den context bilgisi alır
     */
    getContextFromState(key) {
        if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            return state[key] || '';
        }
        return '';
    }
    
  /* =========================================================================
   * 3) Servis Durumu | Service Status
   * ========================================================================= */

    /**
     * checkAIServiceStatus - AI servisinin durumunu kontrol eder ve UI'yı günceller
     */
    async checkAIServiceStatus() {
        
        try {
            // AI service'in status check'ini bekle
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Service'ten direkt durumu kontrol et
            await this.aiChatService.checkServiceStatus();
            const isEnabled = this.aiChatService.isServiceEnabled();
            
            if (!isEnabled) {
                console.warn('[AIChatManager] AI Chat Service is not available');
                this.showServiceUnavailableMessage();
                this.disableChat();
            } else {
                this.hideServiceUnavailableMessage();
                this.enableChat();
            }
        } catch (error) {
            console.error('[AIChatManager] Error checking AI service status:', error);
            this.showServiceUnavailableMessage();
            this.disableChat();
        }
    }
    
    /**
     * enableChat - Chat'i aktif hale getirir
     */
    enableChat() {
        
        if (this.inputField) {
            this.inputField.disabled = false;
            this.inputField.placeholder = "Daima'ya soru sor veya yardım iste...";
        }
        
        if (this.sendButton) {
            this.sendButton.disabled = false;
        }
        
        if (this.quickActionButtons && this.quickActionButtons.length > 0) {
            this.quickActionButtons.forEach(button => {
                button.disabled = false;
            });
        }
    }
    
    /**
     * disableChat - Chat'i deaktif hale getirir
     */
    disableChat() {
        
        if (this.inputField) {
            this.inputField.disabled = true;
            this.inputField.placeholder = "AI sohbet servisi kullanılamıyor...";
        }
        
        if (this.sendButton) {
            this.sendButton.disabled = true;
        }
        
        if (this.quickActionButtons && this.quickActionButtons.length > 0) {
            this.quickActionButtons.forEach(button => {
                button.disabled = true;
            });
        }
    }
    
    /**
     * showServiceUnavailableMessage - Servis kullanılamıyor mesajını gösterir
     */
    showServiceUnavailableMessage() {
        if (this.chatContainer) {
            const existingMessage = this.chatContainer.querySelector('.service-unavailable-message');
            if (!existingMessage) {
                const message = document.createElement('div');
                message.className = 'service-unavailable-message alert alert-warning mb-3';
                message.innerHTML = `
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    AI sohbet servisi şu anda kullanılamıyor.
                `;
                this.chatContainer.prepend(message);
            }
        }
    }
    
    /**
     * hideServiceUnavailableMessage - Servis kullanılamıyor mesajını gizler
     */
    hideServiceUnavailableMessage() {
        if (this.chatContainer) {
            const message = this.chatContainer.querySelector('.service-unavailable-message');
            if (message) {
                message.remove();
            }
        }
    }

    /**
     * setupEventListeners - Event listener'ları ayarlar
     */
    setupEventListeners() {
        
        // Send butonu
        this.sendButton?.addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter tuşu ile mesaj gönderme
        this.inputField?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Input field otomatik boyutlandırma
        this.inputField?.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
    }

    /**
     * setupQuickActions - Hızlı eylem butonlarını ayarlar
     */
    setupQuickActions() {
        
        this.quickActionButtons.forEach(button => {
            button.addEventListener('click', () => {
                const action = button.getAttribute('data-action');
                this.handleQuickAction(action);
            });
        });
    }

    /**
     * handleQuickAction - Hızlı eylem handler'ı
     */
    async handleQuickAction(action) {
        if (!this.sessionId) {
            this.getSessionId();
            if (!this.sessionId) {
                this.addMessage('system', 'Quiz session bilgisi bulunamadı. Lütfen sayfayı yenileyin. 🔄');
                return;
            }
        }
        
        // Chat session'ı başlat (eğer başlatılmamışsa)
        await this.initializeChatSession();
        
        // Bu soru için unique request ID oluştur
        const requestId = ++this.requestCounter;
        this.pendingRequests.set(this.currentQuestionId, requestId);
        
        // AI status'u "Düşünüyor..." olarak güncelle
        this.updateAIStatus('thinking', 'Düşünüyor...');
        
        // Loading durumu göster
        this.showTyping();
        
        // Her quick action mesajı gönderilsin (ilk etkileşim kontrolü kaldırıldı)
        const isFirstMessage = !this.firstInteractionSent.has(this.currentQuestionId);
        
        try {
            // Eylem verisi paketini hazırla
            const actionData = {
                action: action,
                questionId: this.currentQuestionId,
                isFirstMessage: isFirstMessage,
                questionContext: this.aiChatService.getCurrentQuestionData(),
                userAction: {
                    type: 'quick_action',
                    trigger: 'button_click',
                    action_name: action,
                    context: {
                        buttonId: `quick-action-${action}`,
                        timestamp: Date.now()
                    }
                }
            };
            
            const response = await this.aiChatService.sendQuickAction(actionData);
            
            // Typing'i gizle
            this.hideTyping();
            
            // Request geçerliliğini kontrol et
            const currentRequestId = this.pendingRequests.get(this.currentQuestionId);
            if (currentRequestId !== requestId) {
                return; // Bu request artık geçerli değil, cevabı gösterme
            }
            
            // Request'i temizle
            this.pendingRequests.delete(this.currentQuestionId);
            
            // İlk etkileşim başarıyla gönderildiyse işaretle
            if (isFirstMessage) {
                this.firstInteractionSent.add(this.currentQuestionId);
            }
            
            // AI cevabını göster
            if (response.success && response.message) {
                const actionText = 'Açıklama';
                this.addMessage('ai', response.message, actionText);
            } else {
                this.addMessage('system', `Üzgünüm, ${action} alınamadı: ${response.error || 'Bilinmeyen hata'}`);
            }
            
            // Typing durumunu gizle
            this.hideTyping();
        } catch (error) {
            this.hideTyping();
            
            // Request'i temizle
            this.pendingRequests.delete(this.currentQuestionId);
            
            this.addMessage('system', 'Bağlantı hatası. Lütfen tekrar deneyin. 😞');
        }
    }

  /* =========================================================================
   * 5) Yardımcılar | Helpers
   * ========================================================================= */

    /**
     * showWelcomeMessage - Hoş geldin mesajını gösterir
     */
    showWelcomeMessage() {
        
        if (this.aiChatService.isServiceEnabled()) {
            this.addMessage('ai', 'Merhaba! Ben Daima, senin AI öğretmenin! Sorularınla ilgili yardıma ihtiyacın var mı? 🤖✨');
        } else {
            this.addMessage('system', 'AI Chat servisi şu anda kullanılamıyor. 😔');
        }
    }

  /* =========================================================================
   * 4) Chat Etkileşimleri | Chat Interactions
   * ========================================================================= */

    /**
     * sendMessage - Mesaj gönderir
     */
    async sendMessage() {
        
        const message = this.inputField?.value?.trim();
        
        if (!message) return;
        
        // Session ID kontrolü
        if (!this.sessionId) {
            this.getSessionId(); // Tekrar dene
            if (!this.sessionId) {
                this.addMessage('system', 'Quiz session bilgisi bulunamadı. Lütfen sayfayı yenileyin. 🔄');
                return;
            }
        }
        
        // Chat session'ı başlat (eğer başlatılmamışsa)
        await this.initializeChatSession();
        
        // Kullanıcı mesajını ekle
        this.addMessage('user', message);
        this.inputField.value = '';
        this.autoResizeTextarea();
        
        // Bu soru için unique request ID oluştur
        const requestId = ++this.requestCounter;
        this.pendingRequests.set(this.currentQuestionId, requestId);
        
        // Debug: Pending requests durumunu göster
        // this.debugPendingRequests(); // no-op in production
        
        // AI status'u "Düşünüyor..." olarak güncelle
        this.updateAIStatus('thinking', 'Düşünüyor...');
        
        // Loading durumu göster
        this.showTyping();
        
        // Her direct mesaj gönderilsin (ilk mesaj kontrolü kaldırıldı)
        const isFirstMessage = !this.firstUserMessageSent.has(this.currentQuestionId);
        
        try {
            // Mesaj verisi paketini hazırla
            const messageData = {
                message: message,
                questionId: this.currentQuestionId,
                isFirstMessage: isFirstMessage,
                scenarioType: 'direct',
                questionContext: this.aiChatService.getCurrentQuestionData(),
                userAction: {
                    type: 'direct_message',
                    trigger: 'user_input',
                    context: {
                        inputMethod: 'text_input',
                        messageLength: message.length
                    }
                }
            };
            
            // AI'dan yanıt al
            const response = await this.aiChatService.sendChatMessage(messageData);
            
            // Typing'i gizle
            this.hideTyping();
            
            // Request geçerliliğini kontrol et
            const currentRequestId = this.pendingRequests.get(this.currentQuestionId);
            if (currentRequestId !== requestId) {
                return; // Bu request artık geçerli değil, cevabı gösterme
            }
            
            // Request'i temizle
            this.pendingRequests.delete(this.currentQuestionId);
            
            // İlk kullanıcı mesajı başarıyla gönderildiyse işaretle
            if (isFirstMessage) {
                this.firstUserMessageSent.add(this.currentQuestionId);
            }
            
            // AI cevabını göster
            if (response.success && response.message) {
                this.addMessage('ai', response.message);
            } else {
                this.addMessage('system', `Üzgünüm, mesaj gönderilemedi: ${response.error || 'Bilinmeyen hata'}`);
            }
            
            // Typing durumunu gizle
            this.hideTyping();
        } catch (error) {
            this.hideTyping();
            
            // Request'i temizle
            this.pendingRequests.delete(this.currentQuestionId);
            
            this.addMessage('system', 'Bağlantı hatası. Lütfen tekrar deneyin. 😞');
        }
    }

  /* =========================================================================
   * 5) Yardımcılar | Helpers
   * ========================================================================= */

    /**
     * addMessage - Mesaj ekler
     */
    addMessage(type, content, label = null, isFromHistory = false) {
        
        if (!this.messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        
        if (type === 'ai') {
            messageDiv.className = 'ai-message';
            messageDiv.innerHTML = `
                <div class="ai-message-content">
                    <div class="ai-message-text"></div>
                    ${label ? `<div class="ai-message-label">${label}</div>` : ''}
                </div>
            `;
            
            this.messagesContainer.appendChild(messageDiv);
            this.scrollToBottom();
            
            // Typewriter efekti sadece yeni mesajlar için (geçmiş mesajlar için değil)
            const textElement = messageDiv.querySelector('.ai-message-text');
            if (isFromHistory) {
                // Geçmiş mesajları direkt göster
                textElement.innerHTML = this.formatMessage(content);
            } else {
                // Yeni mesajlar için typewriter efekti başlarken status'u "Yazıyor..." yap
                this.updateAIStatus('typing', 'Yazıyor...');
                this.typewriterEffect(textElement, this.formatMessage(content));
            }
            
        } else if (type === 'user') {
            messageDiv.className = 'user-message';
            messageDiv.innerHTML = `
                <div class="user-message-content">
                    <div class="user-message-text">${this.formatMessage(content)}</div>
                </div>
            `;
            
            this.messagesContainer?.appendChild(messageDiv);
            this.scrollToBottom();
        } else if (type === 'system') {
            const currentTime = new Date().toLocaleTimeString('tr-TR', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            messageDiv.className = 'system-message';
            messageDiv.innerHTML = `
                <div class="system-message-content">
                    <div class="system-message-text">${content}</div>
                    <div class="system-message-time">${currentTime}</div>
                </div>
            `;
            
            this.messagesContainer?.appendChild(messageDiv);
            this.scrollToBottom();
        }
    }

    /**
     * typewriterEffect - Typewriter efekti ile metni yazar
     */
    typewriterEffect(element, text, speed = 15) {
        let index = 0;
        
        const typeInterval = setInterval(() => {
            if (index < text.length) {
                element.innerHTML = text.substring(0, index + 1);
                index++;
                // Her karakter yazılırken scroll yap
                this.scrollToBottom();
            } else {
                // Typewriter efekti tamamlandığında status'u "Çevrimiçi" yap
                this.updateAIStatus('online', 'Çevrimiçi');
                clearInterval(typeInterval);
            }
        }, speed);
    }

    /**
     * showTyping - Typing göstergesi ekler (sadece dots, status güncelleme yok)
     */
    showTyping() {
        console.log('[AIChatManager] showTyping called');
        
        if (document.querySelector('.typing-indicator')) {
            console.log('[AIChatManager] Typing indicator already exists, skipping');
            return;
        }
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'ai-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="ai-message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.messagesContainer?.appendChild(typingDiv);
        this.scrollToBottom();
        console.log('[AIChatManager] Typing indicator added to DOM');
    }

    /**
     * hideTyping - Typing göstergesini kaldırır (status güncelleme yok)
     */
    hideTyping() {
        console.log('[AIChatManager] hideTyping called');
        
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
            console.log('[AIChatManager] Typing indicator removed from DOM');
        } else {
            console.log('[AIChatManager] No typing indicator found to remove');
        }
        
        // Status güncelleme kaldırıldı - typewriter efekti tamamlandığında güncellenir
    }
    
    /**
     * updateAIStatus - AI status göstergesini günceller
     */
    updateAIStatus(status, text) {
        console.log(`[AIChatManager] Updating AI status: ${status} - ${text}`);
        
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-text');
        
        if (statusIndicator && statusText) {
            // Önceki class'ları temizle
            statusIndicator.className = 'status-indicator';
            
            // Yeni status class'ını ekle
            statusIndicator.classList.add(status);
            
            // Status text'ini güncelle
            statusText.textContent = text;
            
            console.log(`[AIChatManager] Status updated successfully to: ${status}`);
        } else {
            console.warn('[AIChatManager] Status elements not found!', {
                statusIndicator: !!statusIndicator,
                statusText: !!statusText
            });
        }
    }

    /**
     * formatMessage - Mesajı formatlar
     */
    formatMessage(message) {
        return message
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    /**
     * autoResizeTextarea - Textarea'yı otomatik boyutlandırır
     */
    autoResizeTextarea() {
        if (this.inputField) {
            this.inputField.style.height = 'auto';
            this.inputField.style.height = Math.min(this.inputField.scrollHeight, 120) + 'px';
        }
    }

    /**
     * clearChat - Chat'i temizler
     */
    clearChat() {
        
        if (this.messagesContainer) {
            this.messagesContainer.innerHTML = '';
        }
        
        // Bekleyen request'leri de temizle
        if (this.currentQuestionId && this.pendingRequests.has(this.currentQuestionId)) {
            this.pendingRequests.delete(this.currentQuestionId);
        }
    }
    
    /**
     * scrollToBottom - Mesaj container'ını alta kaydırır
     */
    scrollToBottom() {
        if (this.messagesContainer) {
            // Force container to maintain minimum height before scrolling
            const container = this.messagesContainer.parentElement;
            if (container && container.classList.contains('ai-chat-messages-container')) {
                container.style.minHeight = '350px';
                container.style.height = 'auto';
            }
            
            this.messagesContainer.scrollTo({
                top: this.messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }
    }
    
    /**
     * debugPendingRequests - Debug: Pending requests durumunu gösterir
     */
    debugPendingRequests() {
        // no-op in production
    }
}

/* =========================================================================
 * 6) Dışa Aktarım | Export
 * ========================================================================= */

// Export for ES6 modules (default export)
export default AIChatManager;

// Export for CommonJS (Node.js compatibility)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIChatManager;
}