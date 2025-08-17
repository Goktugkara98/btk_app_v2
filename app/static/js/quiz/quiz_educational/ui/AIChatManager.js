import AnswerMapper from '../utils/AnswerMapper.js';
import ValidationHelpers from '../utils/ValidationHelpers.js';
import ChatUIRenderer from './components/ChatUIRenderer.js';
import QuickActionMessages from '../utils/QuickActionMessages.js';

/**
 * =============================================================================
 * AIChatManager – AI Sohbet Yöneticisi | AI Chat Manager (Refactored)
 * =============================================================================
 * Eğitim modunda AI sohbet arayüzünü ve etkileşim akışını yönetir.
 * Legacy kod temizlenmiş, modüler yapıya dönüştürülmüş versiyon.
 *
 * İÇİNDEKİLER | TABLE OF CONTENTS
 * 1) Kurulum ve Başlatma | Setup & Initialization
 * 2) Oturum ve Soru Bağlamı | Session & Question Context  
 * 3) Servis Durumu | Service Status
 * 4) Chat Etkileşimleri | Chat Interactions
 * 5) Yardımcılar | Helpers
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
        
        // Request tracking
        this.pendingRequests = new Map();
        this.requestCounter = 0;
        
        // İlk etkileşim takibi
        this.firstInteractionSent = new Set();
        this.firstUserMessageSent = new Set();
        
        // Anti-spam kontrolleri
        this.cooldowns = new Map();
        this.COOLDOWN_MS = 4000;
        this.lastMessageByQuestion = new Map();
        
        // UI elementleri
        this.initializeElements();
        
        // UI Renderer'ı başlat
        this.uiRenderer = new ChatUIRenderer({
            messagesContainer: this.messagesContainer,
            inputField: this.inputField,
            sendButton: this.sendButton,
            quickActionButtons: this.quickActionButtons
        });
        
        this.initialize();
    }

    initializeElements() {
        this.chatContainer = document.getElementById('ai-chat-container');
        this.messagesContainer = document.getElementById('ai-chat-messages');
        this.inputField = document.getElementById('ai-chat-input');
        this.sendButton = document.getElementById('ai-send-button');
        this.quickActionButtons = document.querySelectorAll('.quick-action-btn');
    }

    initialize() {
        this.setupEventListeners();
        this.setupQuickActions();
        this.disableChat();
        this.checkAIServiceStatus();
        this.sessionId = ValidationHelpers.getSessionId();
        this.setupMainEventListeners();
    }
    
    setupMainEventListeners() {
        this.eventBus.subscribe('quiz:questionsLoaded', () => {
            this.onQuizLoaded();
        });
        
        this.eventBus.subscribe('question:rendered', (data) => {
            this.onQuestionRendered(data);
        });
        
        this.eventBus.subscribe('answer:wrong', (data) => {
            this.onWrongAnswer(data);
        });
    }
    
  /* =========================================================================
   * 2) Oturum ve Soru Bağlamı | Session & Question Context
   * ========================================================================= */

    onQuizLoaded() {
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
    
    async onQuestionRendered(data) {
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
        
        if (!newQuestionId) {
            newQuestionId = data.questionId || data.question?.id || data.id;
        }
        
        if (this.currentQuestionId === newQuestionId) {
            return;
        }
        
        // Önceki soru için cleanup
        if (this.currentQuestionId) {
            this.pendingRequests.delete(this.currentQuestionId);
            
            const messageController = this.aiChatService.messageControllers.get(this.currentQuestionId);
            if (messageController) {
                messageController.abort();
                this.aiChatService.messageControllers.delete(this.currentQuestionId);
            }
            
            const quickActionController = this.aiChatService.quickActionControllers.get(this.currentQuestionId);
            if (quickActionController) {
                quickActionController.abort();
                this.aiChatService.quickActionControllers.delete(this.currentQuestionId);
            }
        }
        
        this.aiChatService.endChatSession();
        this.currentQuestionId = newQuestionId;
        
        await this.checkAndLoadChatSession();
    }
    
    async checkAndLoadChatSession() {
        if (!this.sessionId || !this.currentQuestionId) {
            console.warn('[AIChatManager] Cannot check chat session - missing sessionId or questionId');
            return;
        }
        
        try {
            const response = await this.aiChatService.getChatHistory(this.currentQuestionId);
            
            if (response.success && response.messages && response.messages.length > 0) {
                this.uiRenderer.clearChat();

                const filtered = response.messages.filter(m => m.role === 'user' || m.role === 'ai');
                filtered.forEach(msg => {
                    this.uiRenderer.addMessage(msg.role, msg.content, msg.label, true);
                });
                
                if (filtered.length === 0) {
                    this.uiRenderer.showWelcomeMessage();
                }

                const hasUser = filtered.some(m => m.role === 'user');
                const hasAI = filtered.some(m => m.role === 'ai');
                if (hasUser || hasAI) this.firstInteractionSent.add(this.currentQuestionId);
                if (hasUser) this.firstUserMessageSent.add(this.currentQuestionId);

            } else {
                this.uiRenderer.clearChat();
                this.firstInteractionSent.delete(this.currentQuestionId);
                this.firstUserMessageSent.delete(this.currentQuestionId);
                this.uiRenderer.showWelcomeMessage();
            }
        } catch (error) {
            console.error('[AIChatManager] Error checking chat session:', error);
            this.uiRenderer.clearChat();
            this.uiRenderer.showWelcomeMessage();
        }
    }
    
  /* =========================================================================
   * 3) Servis Durumu | Service Status
   * ========================================================================= */

    async checkAIServiceStatus() {
        try {
            await new Promise(resolve => setTimeout(resolve, 2000));
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
    
    enableChat() {
        this.uiRenderer.toggleChatControls(true);
    }
    
    disableChat() {
        this.uiRenderer.toggleChatControls(false);
    }
    
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
    
    hideServiceUnavailableMessage() {
        if (this.chatContainer) {
            const message = this.chatContainer.querySelector('.service-unavailable-message');
            if (message) {
                message.remove();
            }
        }
    }

  /* =========================================================================
   * 4) Chat Etkileşimleri | Chat Interactions
   * ========================================================================= */

    async onWrongAnswer(data) {
        await this.initializeChatSession();
        
        const qData = this.aiChatService.getCurrentQuestionData();
        const options = qData?.options || [];
        const { userAnswerText, correctAnswerText } = AnswerMapper.mapAnswerIdsToTexts(
            data.userAnswer, 
            data.correctAnswer, 
            options
        );
        
        const message = `Yine yanlış yaptım. "${userAnswerText}" dedim ama "${correctAnswerText}" doğruymuş. Mantığını anlayamadım, farklı açıklar mısın?`;

        const qId = data.questionId || this.currentQuestionId;
        if (!qId) {
            console.warn('[AIChatManager] Missing questionId for wrong answer event');
            return;
        }

        // Anti-spam kontrolleri
        if (ValidationHelpers.checkCooldown(qId, this.cooldowns, this.COOLDOWN_MS)) {
            console.warn('[AIChatManager] Skipping due to cooldown for question', qId);
            return;
        }
        
        if (ValidationHelpers.isDuplicateMessage(qId, message, this.lastMessageByQuestion)) {
            console.warn('[AIChatManager] Skipping duplicate message for question', qId);
            return;
        }
        
        if (ValidationHelpers.hasPendingRequest(qId, this.pendingRequests)) {
            console.warn('[AIChatManager] Skipping: request already pending for question', qId);
            return;
        }

        this.pendingRequests.set(qId, ++this.requestCounter);
        this.lastMessageByQuestion.set(qId, message);
        
        this.uiRenderer.updateAIStatus('thinking', 'Düşünüyor...');
        this.uiRenderer.showTyping();
        
        try {
            const isFirstForInteraction = !this.firstInteractionSent.has(qId);
            
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
                        selectedAnswer: userAnswerText,
                        correctAnswer: correctAnswerText,
                        timestamp: Date.now()
                    }
                }
            };
            
            const response = await this.aiChatService.sendChatMessage(messageData);
            
            if (response.success) {
                this.uiRenderer.addMessage('ai', response.message || 'Yanlış cevabınızı analiz ediyorum...');
                this.firstInteractionSent.add(qId);
                this.cooldowns.set(qId, Date.now());
            } else {
                console.error('[AIChatManager] Failed to send wrong answer message:', response.error);
                this.uiRenderer.addMessage('error', 'Yanlış cevap analizi başlatılamadı.');
            }
            
            this.uiRenderer.hideTyping();
        } catch (error) {
            console.error('[AIChatManager] Error sending wrong answer message:', error);
            this.uiRenderer.addMessage('error', 'Yanlış cevap bilgisi gönderilirken bir hata oluştu.');
            this.uiRenderer.hideTyping();
        } finally {
            this.pendingRequests.delete(qId);
        }
    }
    
    async initializeChatSession() {
        if (!this.sessionId || !this.currentQuestionId || !this.aiChatService.isServiceEnabled()) {
            console.warn('[AIChatManager] Cannot initialize chat session - missing sessionId, questionId or service disabled');
            return;
        }

        try {
            const context = ValidationHelpers.prepareQuizContext();
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

    async sendMessage() {
        const message = this.inputField?.value?.trim();
        
        if (!message) return;
        
        if (!this.sessionId) {
            this.sessionId = ValidationHelpers.getSessionId();
            if (!this.sessionId) {
                this.uiRenderer.addMessage('system', 'Quiz session bilgisi bulunamadı. Lütfen sayfayı yenileyin. 🔄');
                return;
            }
        }
        
        await this.initializeChatSession();
        
        this.uiRenderer.addMessage('user', message);
        this.inputField.value = '';
        this.uiRenderer.autoResizeTextarea();
        
        const requestId = ++this.requestCounter;
        this.pendingRequests.set(this.currentQuestionId, requestId);
        
        this.uiRenderer.updateAIStatus('thinking', 'Düşünüyor...');
        this.uiRenderer.showTyping();
        
        const isFirstMessage = !this.firstUserMessageSent.has(this.currentQuestionId);
        
        try {
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
            
            const response = await this.aiChatService.sendChatMessage(messageData);
            
            this.uiRenderer.hideTyping();
            
            const currentRequestId = this.pendingRequests.get(this.currentQuestionId);
            if (currentRequestId !== requestId) {
                return;
            }
            
            this.pendingRequests.delete(this.currentQuestionId);
            
            if (isFirstMessage) {
                this.firstUserMessageSent.add(this.currentQuestionId);
            }
            
            if (response.success && response.message) {
                this.uiRenderer.addMessage('ai', response.message);
            } else {
                this.uiRenderer.addMessage('system', `Üzgünüm, mesaj gönderilemedi: ${response.error || 'Bilinmeyen hata'}`);
            }
            
        } catch (error) {
            this.uiRenderer.hideTyping();
            this.pendingRequests.delete(this.currentQuestionId);
            this.uiRenderer.addMessage('system', 'Bağlantı hatası. Lütfen tekrar deneyin. 😞');
        }
    }

    async handleQuickAction(action) {
        if (!this.sessionId) {
            this.sessionId = ValidationHelpers.getSessionId();
            if (!this.sessionId) {
                this.uiRenderer.addMessage('system', 'Quiz session bilgisi bulunamadı. Lütfen sayfayı yenileyin. 🔄');
                return;
            }
        }
        
        await this.initializeChatSession();
        
        const requestId = ++this.requestCounter;
        this.pendingRequests.set(this.currentQuestionId, requestId);
        
        this.uiRenderer.updateAIStatus('thinking', 'Düşünüyor...');
        this.uiRenderer.showTyping();
        
        const isFirstMessage = !this.firstInteractionSent.has(this.currentQuestionId);
        
        try {
            // Custom user mesajını hazırla
            const userMessage = QuickActionMessages.getUserMessage(action);
            
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
                },
                user_message: userMessage  // Custom mesajı backend'e gönder
            };
            
            const response = await this.aiChatService.sendQuickAction(actionData);
            
            this.uiRenderer.hideTyping();
            
            const currentRequestId = this.pendingRequests.get(this.currentQuestionId);
            if (currentRequestId !== requestId) {
                return;
            }
            
            this.pendingRequests.delete(this.currentQuestionId);
            
            if (isFirstMessage) {
                this.firstInteractionSent.add(this.currentQuestionId);
            }
            
            if (response.success && response.message) {
                // Kullanıcı mesajı zaten sendChatMessage ile gönderildi, sadece AI yanıtını göster
                const actionLabel = QuickActionMessages.getActionLabel(action);
                this.uiRenderer.addMessage('ai', response.message, actionLabel);
            } else {
                this.uiRenderer.addMessage('system', `Üzgünüm, ${action} alınamadı: ${response.error || 'Bilinmeyen hata'}`);
            }
            
        } catch (error) {
            this.uiRenderer.hideTyping();
            this.pendingRequests.delete(this.currentQuestionId);
            this.uiRenderer.addMessage('system', 'Bağlantı hatası. Lütfen tekrar deneyin. 😞');
        }
    }

  /* =========================================================================
   * 5) Yardımcılar | Helpers
   * ========================================================================= */

    setupEventListeners() {
        this.sendButton?.addEventListener('click', () => {
            this.sendMessage();
        });

        this.inputField?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.inputField?.addEventListener('input', () => {
            this.uiRenderer.autoResizeTextarea();
        });
    }

    setupQuickActions() {
        this.quickActionButtons.forEach(button => {
            button.addEventListener('click', () => {
                const action = button.getAttribute('data-action');
                this.handleQuickAction(action);
            });
        });
    }
}

export default AIChatManager;
