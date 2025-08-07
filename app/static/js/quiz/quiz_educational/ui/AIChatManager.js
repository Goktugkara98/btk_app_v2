/**
 * AI Chat UI Manager
 * Educational quiz modunda AI sohbet arayüzünü yönetir
 */

class AIChatManager {
    constructor(eventBus, aiChatService) {
        this.eventBus = eventBus;
        this.aiChatService = aiChatService;
        this.currentQuestionId = null;
        this.sessionId = null;
        
        // Pending request tracking için yeni özellikler
        this.pendingRequests = new Map(); // questionId -> requestId mapping
        this.requestCounter = 0; // Unique request ID'ler için
        
        // İlk mesaj takibi için yeni özellikler
        this.firstMessageSent = new Set(); // Her soru için ilk mesaj gönderilip gönderilmediğini takip eder
        
        // UI elementleri
        this.chatContainer = document.getElementById('ai-chat-container');
        this.messagesContainer = document.getElementById('ai-chat-messages');
        this.inputField = document.getElementById('ai-chat-input');
        this.sendButton = document.getElementById('ai-send-button');
        this.quickActionButtons = document.querySelectorAll('.quick-action-btn');
        
        console.log('[AIChatManager] Constructor initialized');
        this.initialize();
    }

    /**
     * AI Chat Manager'ı başlatır
     */
    initialize() {
        console.log('[AIChatManager] Initializing...');
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
        console.log('[AIChatManager] Initialization completed');
    }
    
    /**
     * Ana event listener'ları ayarlar
     */
    setupMainEventListeners() {
        console.log('[AIChatManager] Setting up main event listeners');
        
        // Quiz yüklendiğinde
        this.eventBus.subscribe('quiz:questionsLoaded', () => {
            console.log('[AIChatManager] Quiz loaded event received');
            this.onQuizLoaded();
        });
        
        // Soru render edildiğinde (her soru değişikliğinde)
        this.eventBus.subscribe('question:rendered', (data) => {
            console.log('[AIChatManager] Question rendered event received:', data);
            this.onQuestionRendered(data);
        });
        
        // Yanlış cevap verildiğinde (eski event)
        this.eventBus.subscribe('answer:incorrect', (data) => {
            console.log('[AIChatManager] Incorrect answer event received:', data);
            this.onIncorrectAnswer(data);
        });
        
        // Yanlış cevap verildiğinde (yeni event)
        this.eventBus.subscribe('answer:wrong', (data) => {
            console.log('[AIChatManager] Wrong answer event received:', data);
            this.onWrongAnswer(data);
        });
    }
    
    /**
     * Quiz yüklendiğinde çağrılır
     */
    onQuizLoaded() {
        console.log('[AIChatManager] onQuizLoaded called');
        
        // İlk soru ID'sini al
        if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            console.log('[AIChatManager] StateManager state:', state);
            
            if (state && state.questions && state.questions.length > 0) {
                this.currentQuestionId = state.questions[0].question.id;
                console.log('[AIChatManager] First question ID set:', this.currentQuestionId);
            }
        }
    }
    
    /**
     * Soru render edildiğinde çağrılır (her soru değişikliğinde)
     */
    async onQuestionRendered(data) {
        console.log('[AIChatManager] onQuestionRendered called with data:', data);
        
        // StateManager'dan current question ID'yi al
        let newQuestionId = null;
        if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            console.log('[AIChatManager] Current state:', state);
            
            if (state && state.currentQuestion && state.currentQuestion.question) {
                newQuestionId = state.currentQuestion.question.id;
                console.log('[AIChatManager] Question ID from StateManager:', newQuestionId);
            }
        }
        
        // Eğer StateManager'dan alamadıysak, event data'dan al
        if (!newQuestionId) {
            newQuestionId = data.questionId || data.question?.id || data.id;
            console.log('[AIChatManager] Question ID from event data:', newQuestionId);
        }
        
        // Eğer aynı soru için tekrar çağrılıyorsa, işlem yapma
        if (this.currentQuestionId === newQuestionId) {
            console.log('[AIChatManager] Same question detected, skipping chat session check');
            return;
        }
        
        // Önceki soru için bekleyen request'leri temizle
        if (this.currentQuestionId && this.pendingRequests.has(this.currentQuestionId)) {
            console.log('[AIChatManager] Clearing pending requests for previous question:', this.currentQuestionId);
            this.pendingRequests.delete(this.currentQuestionId);
        }
        
        // Yeni soru ID'sini güncelle
        this.currentQuestionId = newQuestionId;
        console.log('[AIChatManager] Final question ID:', this.currentQuestionId);
        
        // Debug: Pending requests durumunu göster
        this.debugPendingRequests();
        
        // Bu soru için chat session'ı kontrol et ve gerekirse yükle
        await this.checkAndLoadChatSession();
    }
    
    /**
     * Bu soru için chat session'ı kontrol eder ve gerekirse yükler
     */
    async checkAndLoadChatSession() {
        console.log('[AIChatManager] checkAndLoadChatSession called for questionId:', this.currentQuestionId);
        
        if (!this.sessionId || !this.currentQuestionId) {
            console.warn('[AIChatManager] Cannot check chat session - missing sessionId or questionId');
            return;
        }
        
        try {
            // Bu soru için chat history'yi kontrol et
            const response = await this.aiChatService.getChatHistory(this.currentQuestionId);
            console.log('[AIChatManager] Chat history check response:', response);
            
            if (response.success && response.messages && response.messages.length > 0) {
                console.log('[AIChatManager] Chat history found, loading messages:', response.messages.length);
                
                // Chat'i temizle
                this.clearChat();
                
                // Mesajları yükle
                response.messages.forEach(msg => {
                    this.addMessage(msg.role, msg.content, msg.label);
                });
                
                // Bu soru için ilk mesaj gönderilmiş olarak işaretle
                this.firstMessageSent.add(this.currentQuestionId);
                
                console.log('[AIChatManager] Chat history loaded successfully');
            } else {
                console.log('[AIChatManager] No chat history found, showing welcome message');
                
                // Chat'i temizle
                this.clearChat();
                
                // Bu soru için ilk mesaj gönderilmemiş olarak işaretle
                this.firstMessageSent.delete(this.currentQuestionId);
                
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
    
    /**
     * Yanlış cevap verildiğinde çağrılır (eski event)
     */
    async onIncorrectAnswer(data) {
        console.log('[AIChatManager] onIncorrectAnswer called with data:', data);
        
        // Chat session'ı başlat (eğer başlatılmamışsa)
        await this.initializeChatSession();
        
        // Yanlış cevap bilgisini AI'ya gönder
        const message = `Kullanıcı yanlış cevap verdi. Soru ID: ${data.questionId}, Kullanıcının cevabı: ${data.userAnswer}, Doğru cevap: ${data.correctAnswer}. Lütfen bu yanlış cevabı analiz et ve kullanıcıya yardımcı ol.`;
        
        try {
            // AI'dan yanıt al
            const response = await this.aiChatService.sendChatMessage(message, this.currentQuestionId);
            
            if (response.success) {
                this.addMessage('ai', response.message);
            } else {
                this.addMessage('system', 'Yanlış cevap analizi yapılamadı.');
            }
        } catch (error) {
            console.error('[AIChatManager] Error in incorrect answer handling:', error);
            this.addMessage('system', 'Yanlış cevap analizi sırasında hata oluştu.');
        }
    }

    /**
     * Yanlış cevap verildiğinde çağrılır (yeni event)
     */
    async onWrongAnswer(data) {
        console.log('[AIChatManager] onWrongAnswer called with data:', data);
        
        // Chat session'ı başlat (eğer başlatılmamışsa)
        await this.initializeChatSession();
        
        // Yanlış cevap bilgisini AI'ya gönder
        const message = `Kullanıcı yanlış cevap verdi. Soru ID: ${data.questionId}, Kullanıcının cevabı: ${data.userAnswer}, Doğru cevap: ${data.correctAnswer?.id || data.correctAnswer}. Lütfen bu yanlış cevabı analiz et ve kullanıcıya yardımcı ol.`;
        
        try {
            // AI'ya mesaj gönder
            const response = await this.aiChatService.sendMessage(message, this.currentQuestionId);
            
            if (response.success) {
                console.log('[AIChatManager] Wrong answer message sent successfully');
                // AI yanıtını chat'e ekle
                this.addMessage('ai', response.message || 'Yanlış cevabınızı analiz ediyorum...');
            } else {
                console.error('[AIChatManager] Failed to send wrong answer message:', response.error);
                this.addMessage('error', 'Yanlış cevap analizi başlatılamadı.');
            }
        } catch (error) {
            console.error('[AIChatManager] Error sending wrong answer message:', error);
            this.addMessage('error', 'Yanlış cevap bilgisi gönderilirken bir hata oluştu.');
        }
    }
    
    /**
     * Session ID'yi window veya StateManager'dan alır
     */
    getSessionId() {
        console.log('[AIChatManager] getSessionId called');
        
        // Önce window.QUIZ_CONFIG'den dene
        if (window.QUIZ_CONFIG && window.QUIZ_CONFIG.sessionId) {
            this.sessionId = window.QUIZ_CONFIG.sessionId;
            console.log('[AIChatManager] Session ID from QUIZ_CONFIG:', this.sessionId);
            return;
        }
        
        // StateManager'dan dene
        if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            if (state && state.sessionId) {
                this.sessionId = state.sessionId;
                console.log('[AIChatManager] Session ID from StateManager:', this.sessionId);
                return;
            }
        }
        
        console.warn('[AIChatManager] Session ID not found');
    }
    
    /**
     * Chat session'ını başlatır
     */
    async initializeChatSession() {
        console.log('[AIChatManager] initializeChatSession called');
        console.log('[AIChatManager] Parameters - sessionId:', this.sessionId, 'questionId:', this.currentQuestionId, 'serviceEnabled:', this.aiChatService.isServiceEnabled());
        
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

            console.log('[AIChatManager] Starting chat session with context:', context);
            const result = await this.aiChatService.startChatSession(this.sessionId, this.currentQuestionId, context);
            console.log('[AIChatManager] Chat session start result:', result);
            
            if (result.success) {
                this.enableChat();
                console.log('[AIChatManager] Chat session initialized successfully');
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
     * State'den context bilgisi alır
     */
    getContextFromState(key) {
        if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            return state[key] || '';
        }
        return '';
    }
    
    /**
     * AI servisinin durumunu kontrol eder ve UI'yı günceller
     */
    async checkAIServiceStatus() {
        console.log('[AIChatManager] checkAIServiceStatus called');
        
        try {
            // AI service'in status check'ini bekle
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Service'ten direkt durumu kontrol et
            await this.aiChatService.checkServiceStatus();
            const isEnabled = this.aiChatService.isServiceEnabled();
            
            console.log('[AIChatManager] AI Service status:', isEnabled);
            
            if (!isEnabled) {
                console.warn('[AIChatManager] AI Chat Service is not available');
                this.showServiceUnavailableMessage();
                this.disableChat();
            } else {
                console.log('[AIChatManager] AI Chat Service is available');
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
     * Chat'i aktif hale getirir
     */
    enableChat() {
        console.log('[AIChatManager] enableChat called');
        
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
     * Chat'i deaktif hale getirir
     */
    disableChat() {
        console.log('[AIChatManager] disableChat called');
        
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
     * Servis kullanılamıyor mesajını gösterir
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
     * Servis kullanılamıyor mesajını gizler
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
     * Event listener'ları ayarlar
     */
    setupEventListeners() {
        console.log('[AIChatManager] setupEventListeners called');
        
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
     * Hızlı eylem butonlarını ayarlar
     */
    setupQuickActions() {
        console.log('[AIChatManager] setupQuickActions called');
        
        this.quickActionButtons.forEach(button => {
            button.addEventListener('click', () => {
                const action = button.getAttribute('data-action');
                this.handleQuickAction(action);
            });
        });
    }

    /**
     * Hoş geldin mesajını gösterir
     */
    showWelcomeMessage() {
        console.log('[AIChatManager] showWelcomeMessage called');
        
        if (this.aiChatService.isServiceEnabled()) {
            this.addMessage('ai', 'Merhaba! Ben Daima, senin AI öğretmenin! Sorularınla ilgili yardıma ihtiyacın var mı? 🤖✨');
        } else {
            this.addMessage('system', 'AI Chat servisi şu anda kullanılamıyor. 😔');
        }
    }

    /**
     * Mesaj gönderir
     */
    async sendMessage() {
        console.log('[AIChatManager] sendMessage called');
        
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
        
        console.log('[AIChatManager] Created request ID:', requestId, 'for question:', this.currentQuestionId);
        console.log('[AIChatManager] Current pending requests:', Array.from(this.pendingRequests.entries()));
        
        // Debug: Pending requests durumunu göster
        this.debugPendingRequests();
        
        // Loading durumu göster
        this.showTyping();
        
        // İlk mesaj kontrolü
        const isFirstMessage = !this.firstMessageSent.has(this.currentQuestionId);
        console.log('[AIChatManager] Is first message for this question:', isFirstMessage);
        
        try {
            // AI'dan yanıt al
            const response = await this.aiChatService.sendChatMessage(
                message, 
                this.currentQuestionId,
                isFirstMessage
            );
            
            this.hideTyping();
            
            // Request'in hala geçerli olup olmadığını kontrol et
            const currentRequestId = this.pendingRequests.get(this.currentQuestionId);
            if (currentRequestId !== requestId) {
                console.log('[AIChatManager] Request outdated. Current:', currentRequestId, 'Response for:', requestId);
                console.log('[AIChatManager] Ignoring response for outdated request');
                return; // Bu request artık geçerli değil, cevabı gösterme
            }
            
            // Request'i temizle
            this.pendingRequests.delete(this.currentQuestionId);
            console.log('[AIChatManager] Request completed and cleared for question:', this.currentQuestionId);
            
            // İlk mesaj başarıyla gönderildiyse işaretle
            if (isFirstMessage) {
                this.firstMessageSent.add(this.currentQuestionId);
                console.log('[AIChatManager] First message sent for question:', this.currentQuestionId);
            }
            
            // AI cevabını göster
            if (response.success && response.message) {
                this.addMessage('ai', response.message);
            } else {
                this.addMessage('system', `Üzgünüm, bir hata oluştu: ${response.error || 'Bilinmeyen hata'}`);
            }
        } catch (error) {
            this.hideTyping();
            
            // Request'i temizle
            this.pendingRequests.delete(this.currentQuestionId);
            console.log('[AIChatManager] Request failed and cleared for question:', this.currentQuestionId);
            
            this.addMessage('system', 'Bağlantı hatası. Lütfen tekrar deneyin. 😞');
        }
    }

    /**
     * Hızlı eylem işler
     */
    async handleQuickAction(action) {
        console.log('[AIChatManager] handleQuickAction called with action:', action);
        
        if (!this.sessionId || !this.currentQuestionId) {
            this.addMessage('system', 'Önce bir soru yüklenmeli. 🤨');
            return;
        }

        // Chat session'ı başlat (eğer başlatılmamışsa)
        await this.initializeChatSession();

        // Bu soru için unique request ID oluştur
        const requestId = ++this.requestCounter;
        this.pendingRequests.set(this.currentQuestionId, requestId);
        
        console.log('[AIChatManager] Created quick action request ID:', requestId, 'for question:', this.currentQuestionId);
        console.log('[AIChatManager] Current pending requests:', Array.from(this.pendingRequests.entries()));

        // Loading durumu göster
        this.showTyping();
        
        // İlk mesaj kontrolü (hızlı eylemler de ilk mesaj sayılabilir)
        const isFirstMessage = !this.firstMessageSent.has(this.currentQuestionId);
        console.log('[AIChatManager] Is first message for quick action:', isFirstMessage);
        
        try {
            const response = await this.aiChatService.sendQuickAction(action, this.currentQuestionId, isFirstMessage);
            
            this.hideTyping();
            
            // Request'in hala geçerli olup olmadığını kontrol et
            const currentRequestId = this.pendingRequests.get(this.currentQuestionId);
            if (currentRequestId !== requestId) {
                console.log('[AIChatManager] Quick action request outdated. Current:', currentRequestId, 'Response for:', requestId);
                console.log('[AIChatManager] Ignoring response for outdated quick action request');
                return; // Bu request artık geçerli değil, cevabı gösterme
            }
            
            // Request'i temizle
            this.pendingRequests.delete(this.currentQuestionId);
            console.log('[AIChatManager] Quick action request completed and cleared for question:', this.currentQuestionId);
            
            // İlk mesaj başarıyla gönderildiyse işaretle
            if (isFirstMessage) {
                this.firstMessageSent.add(this.currentQuestionId);
                console.log('[AIChatManager] First message sent for quick action on question:', this.currentQuestionId);
            }
            
            // AI cevabını göster
            if (response.success && response.message) {
                const actionText = action === 'explain' ? 'Açıklama' : 'İpucu';
                this.addMessage('ai', response.message, actionText);
            } else {
                this.addMessage('system', `Üzgünüm, ${action} alınamadı: ${response.error || 'Bilinmeyen hata'}`);
            }
        } catch (error) {
            this.hideTyping();
            
            // Request'i temizle
            this.pendingRequests.delete(this.currentQuestionId);
            console.log('[AIChatManager] Quick action request failed and cleared for question:', this.currentQuestionId);
            
            this.addMessage('system', 'Bağlantı hatası. Lütfen tekrar deneyin. 😞');
        }
    }

    /**
     * Mesaj ekler
     */
    addMessage(type, content, label = null) {
        if (!this.messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ${type}-message`;
        
        const time = new Date().toLocaleTimeString('tr-TR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        if (type === 'ai') {
            messageDiv.innerHTML = `
                <div class="ai-message-content">
                    ${label ? `<div class="ai-message-label">${label}</div>` : ''}
                    <div class="ai-message-text" id="ai-text-${Date.now()}"></div>
                    <div class="ai-message-time">${time}</div>
                </div>
            `;
            
            this.messagesContainer?.appendChild(messageDiv);
            this.scrollToBottom();
            
            // Typewriter efekti için AI mesajını animasyonlu yaz
            const textElement = messageDiv.querySelector('.ai-message-text');
            this.typewriterEffect(textElement, this.formatMessage(content));
            
        } else if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="user-message-content">
                    <div class="user-message-text">${this.formatMessage(content)}</div>
                    <div class="user-message-time">${time}</div>
                </div>
            `;
            
            this.messagesContainer?.appendChild(messageDiv);
            this.scrollToBottom();
        } else if (type === 'system') {
            messageDiv.innerHTML = `
                <div class="system-message-content">
                    <div class="system-message-text">${content}</div>
                    <div class="system-message-time">${time}</div>
                </div>
            `;
            
            this.messagesContainer?.appendChild(messageDiv);
            this.scrollToBottom();
        }
    }

    /**
     * Typewriter efekti ile metni yazar
     */
    typewriterEffect(element, text, speed = 15) {
        // Metni HTML etiketlerine göre parçalara böl
        const parts = text.split(/(<br>|<strong>|<\/strong>|<em>|<\/em>)/);
        let currentIndex = 0;
        let currentPart = 0;
        
        const typeInterval = setInterval(() => {
            if (currentPart < parts.length) {
                const part = parts[currentPart];
                
                // HTML etiketi ise direkt ekle
                if (part === '<br>' || part === '<strong>' || part === '</strong>' || part === '<em>' || part === '</em>') {
                    element.innerHTML += part;
                    currentPart++;
                } else {
                    // Normal metin ise karakter karakter yaz
                    if (currentIndex < part.length) {
                        element.innerHTML += part.charAt(currentIndex);
                        currentIndex++;
                    } else {
                        currentPart++;
                        currentIndex = 0;
                    }
                }
                
                this.scrollToBottom();
            } else {
                clearInterval(typeInterval);
            }
        }, speed);
    }

    /**
     * Typing göstergesi ekler
     */
    showTyping() {
        if (document.querySelector('.typing-indicator')) return;
        
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
    }

    /**
     * Typing göstergesini kaldırır
     */
    hideTyping() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    /**
     * Mesajı formatlar
     */
    formatMessage(message) {
        return message
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    /**
     * Textarea'yı otomatik boyutlandırır
     */
    autoResizeTextarea() {
        if (this.inputField) {
            this.inputField.style.height = 'auto';
            this.inputField.style.height = Math.min(this.inputField.scrollHeight, 120) + 'px';
        }
    }

    /**
     * Chat'i temizler
     */
    clearChat() {
        console.log('[AIChatManager] clearChat called');
        
        if (this.messagesContainer) {
            this.messagesContainer.innerHTML = '';
        }
        
        // Bekleyen request'leri de temizle
        if (this.currentQuestionId && this.pendingRequests.has(this.currentQuestionId)) {
            console.log('[AIChatManager] Clearing pending requests during chat clear for question:', this.currentQuestionId);
            this.pendingRequests.delete(this.currentQuestionId);
        }
    }
    
    /**
     * Mesaj container'ını alta kaydırır
     */
    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTo({
                top: this.messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }
    }
    
    /**
     * Debug: Pending requests durumunu gösterir
     */
    debugPendingRequests() {
        console.log('[AIChatManager] === PENDING REQUESTS DEBUG ===');
        console.log('[AIChatManager] Current question ID:', this.currentQuestionId);
        console.log('[AIChatManager] Pending requests:', Array.from(this.pendingRequests.entries()));
        console.log('[AIChatManager] Request counter:', this.requestCounter);
        console.log('[AIChatManager] First message sent for questions:', Array.from(this.firstMessageSent));
        console.log('[AIChatManager] ================================');
    }
}

// Export for ES6 modules (default export)
export default AIChatManager;

// Export for CommonJS (Node.js compatibility)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIChatManager;
}