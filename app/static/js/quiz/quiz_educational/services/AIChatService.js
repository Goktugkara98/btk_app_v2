/**
 * AI Chat Service V2
 * Educational quiz modu için AI sohbet hizmetlerini yönetir
 * Yeni modüler API yapısı ile çalışır
 */

class AIChatService {
    constructor() {
        this.baseUrl = '/api/ai';
        this.isEnabled = false;
        this.chatSessionId = null;
        console.log('[AIChatService] Constructor initialized');
        this.checkServiceStatus();
    }

    /**
     * AI servisinin durumunu kontrol eder
     */
    async checkServiceStatus() {
        console.log('[AIChatService] checkServiceStatus called');
        
        try {
            const response = await fetch(`${this.baseUrl}/system/status`);
            const data = await response.json();
            
            console.log('[AIChatService] Status check response:', data);
            
            if (data.status === 'success') {
                this.isEnabled = data.data.available;
                console.log('[AIChatService] Service enabled:', this.isEnabled);
            } else {
                console.warn('[AIChatService] Service check failed:', data.message);
                this.isEnabled = false;
            }
        } catch (error) {
            console.error('[AIChatService] Status check error:', error);
            this.isEnabled = false;
        }
    }

    /**
     * Servisin aktif olup olmadığını döndürür
     */
    isServiceEnabled() {
        console.log('[AIChatService] isServiceEnabled called, returning:', this.isEnabled);
        return this.isEnabled;
    }

    /**
     * Chat session başlatır
     * @param {string} quizSessionId - Quiz session ID
     * @param {number} questionId - Aktif soru ID
     * @param {Object} context - Quiz context bilgileri
     * @returns {Promise<Object>} Session bilgileri
     */
    async startChatSession(quizSessionId, questionId, context = {}) {
        console.log('[AIChatService] startChatSession called with:', { quizSessionId, questionId, context });
        
        if (!this.isEnabled) {
            console.warn('[AIChatService] Cannot start chat session - service not enabled');
            return {
                success: false,
                error: 'AI Chat service is not available'
            };
        }

        try {
            // Quiz session + question ID kombinasyonu olarak chat session ID oluştur
            const chatSessionId = `chat_${quizSessionId}_${questionId}`;
            console.log('[AIChatService] Generated chat session ID:', chatSessionId);
            
            const requestBody = {
                quiz_session_id: quizSessionId,
                question_id: questionId,
                chat_session_id: chatSessionId, // Önceden oluşturulan session ID
                context: context
            };
            
            console.log('[AIChatService] Sending start session request:', requestBody);
            
            const response = await fetch(`${this.baseUrl}/session/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();
            console.log('[AIChatService] Start session response:', data);
            
            if (data.status === 'success') {
                this.chatSessionId = chatSessionId;
                console.log('[AIChatService] Chat session started successfully:', this.chatSessionId);
                return {
                    success: true,
                    chatSessionId: this.chatSessionId
                };
            } else {
                console.error('[AIChatService] Failed to start chat session:', data.message);
                return {
                    success: false,
                    error: data.message || 'Failed to start chat session'
                };
            }
        } catch (error) {
            console.error('[AIChatService] Start chat session error:', error);
            return {
                success: false,
                error: 'Network error occurred'
            };
        }
    }

    /**
     * Chat mesajı gönderir ve AI yanıtı alır
     * @param {string} message - Gönderilecek mesaj
     * @param {number} currentQuestionId - Mevcut soru ID (opsiyonel)
     * @param {boolean} isFirstMessage - İlk mesaj mı (soru ve şıkları eklemek için)
     * @returns {Promise<Object>} AI yanıtı
     */
    async sendChatMessage(message, currentQuestionId = null, isFirstMessage = false) {
        console.log('[AIChatService] sendChatMessage called with:', { message, currentQuestionId, isFirstMessage });
        
        if (!this.isEnabled) {
            throw new Error('AI Chat servisi kullanılamıyor');
        }

        if (!this.chatSessionId) {
            throw new Error('Chat session başlatılmamış');
        }

        if (!message || !message.trim()) {
            throw new Error('Mesaj boş olamaz');
        }

        try {
            const requestBody = {
                message: message.trim(),
                chat_session_id: this.chatSessionId
            };

            if (currentQuestionId) {
                requestBody.question_id = currentQuestionId;
            }

            // İlk mesaj ise soru ve şıkların içeriğini ekle
            if (isFirstMessage && currentQuestionId) {
                const questionData = this.getCurrentQuestionData();
                if (questionData) {
                    requestBody.question_context = {
                        question_text: questionData.question_text,
                        options: questionData.options
                    };
                    console.log('[AIChatService] Added question context for first message:', requestBody.question_context);
                }
            }

            console.log('[AIChatService] Sending chat message:', requestBody);

            const response = await fetch(`${this.baseUrl}/chat/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();
            console.log('[AIChatService] Chat message response:', data);

            if (data.status === 'success') {
                return {
                    success: true,
                    message: data.data.ai_response
                };
            } else {
                throw new Error(data.message || 'AI yanıtı alınamadı');
            }
        } catch (error) {
            console.error('[AIChatService] Send chat message error:', error);
            throw error;
        }
    }

    /**
     * Mevcut sorunun verilerini alır
     * @returns {Object|null} Soru ve şıkların içeriği
     */
    getCurrentQuestionData() {
        try {
            // StateManager'dan mevcut soru bilgilerini al
            if (window.quizApp && window.quizApp.stateManager) {
                const state = window.quizApp.stateManager.getState();
                const currentQuestion = state.currentQuestion;
                
                console.log('[AIChatService] Current question from state:', currentQuestion);
                
                if (currentQuestion && currentQuestion.question) {
                    // QuizEngine'den gelen format: question.text
                    // Ama biz question_text arıyoruz
                    const questionText = currentQuestion.question.text || currentQuestion.question.question_text;
                    
                    // Options'ları al - farklı formatları kontrol et
                    let options = [];
                    if (currentQuestion.question.options && Array.isArray(currentQuestion.question.options)) {
                        options = currentQuestion.question.options;
                    } else if (currentQuestion.options && Array.isArray(currentQuestion.options)) {
                        options = currentQuestion.options;
                    }
                    
                    console.log('[AIChatService] Question text:', questionText);
                    console.log('[AIChatService] Options found:', options.length);
                    console.log('[AIChatService] First option sample:', options[0]);
                    
                    if (questionText && options.length > 0) {
                        const mappedOptions = options.map(option => ({
                            id: option.id,
                            option_text: option.text || option.option_text || option.name,
                            is_correct: option.is_correct
                        }));
                        
                        console.log('[AIChatService] Mapped options:', mappedOptions);
                        
                        return {
                            question_text: questionText,
                            options: mappedOptions
                        };
                    }
                }
            }
            
            console.warn('[AIChatService] Could not get current question data - missing required fields');
            return null;
        } catch (error) {
            console.error('[AIChatService] Error getting current question data:', error);
            return null;
        }
    }

    /**
     * Hızlı eylemler için AI yanıtı alır (açıkla, ipucu)
     * @param {string} action - 'explain' veya 'hint'
     * @param {number} questionId - Soru ID
     * @param {boolean} isFirstMessage - İlk mesaj mı (soru ve şıkları eklemek için)
     * @returns {Promise<Object>} AI yanıtı
     */
    async sendQuickAction(action, questionId, isFirstMessage = false) {
        console.log('[AIChatService] sendQuickAction called with:', { action, questionId, isFirstMessage });
        
        if (!this.isEnabled) {
            console.warn('[AIChatService] Cannot send quick action - service not enabled');
            return {
                success: false,
                error: 'AI Chat service is not available'
            };
        }

        if (!this.chatSessionId) {
            console.warn('[AIChatService] Cannot send quick action - no chat session');
            return {
                success: false,
                error: 'Chat session not started'
            };
        }

        try {
            const requestBody = {
                action: action,
                chat_session_id: this.chatSessionId,
                question_id: questionId
            };
            
            // İlk mesaj ise soru ve şıkların içeriğini ekle
            if (isFirstMessage && questionId) {
                const questionData = this.getCurrentQuestionData();
                if (questionData) {
                    requestBody.question_context = {
                        question_text: questionData.question_text,
                        options: questionData.options
                    };
                    console.log('[AIChatService] Added question context for quick action first message:', requestBody.question_context);
                }
            }
            
            console.log('[AIChatService] Sending quick action request:', requestBody);

            const response = await fetch(`${this.baseUrl}/chat/quick-action`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();
            console.log('[AIChatService] Quick action response:', data);
            
            if (data.status === 'success') {
                return {
                    success: true,
                    message: data.data.ai_response,
                    action: action
                };
            } else {
                console.error('[AIChatService] Quick action failed:', data.message);
                return {
                    success: false,
                    error: data.message || 'Unknown error occurred'
                };
            }
        } catch (error) {
            console.error('[AIChatService] Quick action error:', error);
            return {
                success: false,
                error: 'Network error occurred'
            };
        }
    }

    /**
     * Chat session'ının durumunu kontrol eder
     * @returns {boolean} Session aktif mi
     */
    isSessionActive() {
        const isActive = this.chatSessionId !== null;
        console.log('[AIChatService] isSessionActive called, returning:', isActive, 'sessionId:', this.chatSessionId);
        return isActive;
    }

    /**
     * Chat session'ını sonlandırır
     */
    endChatSession() {
        console.log('[AIChatService] endChatSession called, previous sessionId:', this.chatSessionId);
        this.chatSessionId = null;
        console.log('[AIChatService] Chat session ended');
    }
    
    /**
     * Chat history'yi getirir
     * @param {number} questionId - Soru ID
     * @returns {Promise<Object>} Chat history
     */
    async getChatHistory(questionId) {
        console.log('[AIChatService] getChatHistory called with questionId:', questionId);
        
        if (!this.isEnabled) {
            console.warn('[AIChatService] Cannot get chat history - service not enabled');
            return {
                success: false,
                error: 'AI Chat service is not available'
            };
        }
        
        // Quiz session ID'yi window'dan al
        const quizSessionId = window.QUIZ_CONFIG?.sessionId || window.QUIZ_SESSION_ID;
        console.log('[AIChatService] Quiz session ID from window:', quizSessionId);
        
        if (!quizSessionId) {
            console.error('[AIChatService] Cannot get chat history - no quiz session ID');
            return {
                success: false,
                error: 'Quiz session ID bulunamadı'
            };
        }
        
        // Chat session ID'yi oluştur
        const chatSessionId = `chat_${quizSessionId}_${questionId}`;
        console.log('[AIChatService] Generated chat session ID for history:', chatSessionId);
        
        try {
            const url = `${this.baseUrl}/chat/history?chat_session_id=${chatSessionId}`;
            console.log('[AIChatService] Fetching chat history from:', url);
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            console.log('[AIChatService] Chat history response:', data);
            
            if (data.status === 'success') {
                const messages = data.data.messages || [];
                console.log('[AIChatService] Chat history loaded successfully, message count:', messages.length);
                return {
                    success: true,
                    messages: messages
                };
            } else {
                console.error('[AIChatService] Failed to get chat history:', data.message);
                return {
                    success: false,
                    error: data.message || 'Chat history alınamadı'
                };
            }
        } catch (error) {
            console.error('[AIChatService] Get chat history error:', error);
            return {
                success: false,
                error: 'Network error occurred'
            };
        }
    }

    /**
     * Service health check yapar
     * @returns {Promise<boolean>} Servis sağlıklı mı
     */
    async healthCheck() {
        console.log('[AIChatService] healthCheck called');
        
        try {
            const response = await fetch(`${this.baseUrl}/system/health`);
            const data = await response.json();
            
            const isHealthy = data.status === 'success' && data.data.healthy;
            console.log('[AIChatService] Health check result:', isHealthy);
            
            return isHealthy;
        } catch (error) {
            console.error('[AIChatService] Health check error:', error);
            return false;
        }
    }
}

// Export for ES6 modules (default export)
export default AIChatService;

// Export for CommonJS (Node.js compatibility)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIChatService;
}