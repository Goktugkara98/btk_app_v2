/**
 * AI Chat Service V2
 * Educational quiz modu için AI sohbet hizmetlerini yönetir
 * Yeni modüler API yapısı ile çalışır
 */

/*
 * İÇİNDEKİLER (Table of Contents)
 * - [1] Kurulum
 *   - [1.1] constructor()
 *   - [1.2] checkServiceStatus()
 * - [2] Durum/Yetkinlik
 *   - [2.1] isServiceEnabled()
 * - [3] Oturum
 *   - [3.1] startChatSession(quizSessionId, questionId, context)
 *   - [3.2] isSessionActive()
 *   - [3.3] endChatSession()
 *   - [3.4] getChatHistory(questionId)
 * - [4] Mesajlaşma
 *   - [4.1] sendChatMessage(message, currentQuestionId, isFirstMessage)
 * - [5] Hızlı Eylemler
 *   - [5.1] sendQuickAction(action, questionId, isFirstMessage)
 * - [6] Soru Bağlamı
 *   - [6.1] getCurrentQuestionData()
 * - [7] Sağlık
 *   - [7.1] healthCheck()
 * - [8] Dışa Aktarım
 *   - [8.1] export default
 *   - [8.2] CommonJS export
 */
class AIChatService {
    /**
     * [1.1] constructor - Servis URL'lerini ve kontrol yapılarını kurar; durum kontrolünü başlatır.
     * Kategori: [1] Kurulum
     */
    constructor() {
        this.baseUrl = '/api/ai';
        this.isEnabled = false;
        this.chatSessionId = null;
        // Birden fazla eşzamanlı isteği engellemek için AbortController haritaları
        this.messageControllers = new Map(); // key: questionId | 'default'
        this.quickActionControllers = new Map(); // key: questionId | 'default'
        this.checkServiceStatus();
    }

    /**
     * [1.2] checkServiceStatus - AI servisinin durumunu kontrol eder.
     * Kategori: [1] Kurulum
     */
    async checkServiceStatus() {
        
        try {
            const response = await fetch(`${this.baseUrl}/system/status`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.isEnabled = data.data.available;
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
     * [2.1] isServiceEnabled - Servisin aktif olup olmadığını döndürür.
     * Kategori: [2] Durum/Yetkinlik
     */
    isServiceEnabled() {
        return this.isEnabled;
    }

    /**
     * [3.1] startChatSession - Chat session başlatır.
     * Kategori: [3] Oturum
     * @param {string} quizSessionId - Quiz session ID
     * @param {number} questionId - Aktif soru ID
     * @param {Object} context - Quiz context bilgileri
     * @returns {Promise<Object>} Session bilgileri
     */
    async startChatSession(quizSessionId, questionId, context = {}) {
        
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
            
            const requestBody = {
                quiz_session_id: quizSessionId,
                question_id: questionId,
                chat_session_id: chatSessionId, // Önceden oluşturulan session ID
                context: context
            };
            
            const response = await fetch(`${this.baseUrl}/session/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                // Prefer server-provided chat_session_id if available for robustness
                const serverSessionId = data?.data?.chat_session_id || chatSessionId;
                this.chatSessionId = serverSessionId;
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
     * [4.1] sendChatMessage - Chat mesajı gönderir ve AI yanıtı alır.
     * Kategori: [4] Mesajlaşma
     * @param {string} message - Gönderilecek mesaj
     * @param {number} currentQuestionId - Mevcut soru ID (opsiyonel)
     * @param {boolean} isFirstMessage - İlk mesaj mı (soru ve şıkları eklemek için)
     * @returns {Promise<Object>} AI yanıtı
     */
    async sendChatMessage(message, currentQuestionId = null, isFirstMessage = false) {
        
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
                }
            }

            // Debug: final prompt'u backend response'unda görmek için debug bayrağını gönder
            const debugEnabled = (window.QUIZ_CONFIG?.aiDebug ?? true);
            requestBody.debug = debugEnabled;

            // Giden isteği konsola yaz
            // eslint-disable-next-line no-console
            console.log('[AI Debug] Sending /chat/message request:', requestBody);

            // Aynı soru için önceki isteği iptal et
            const key = currentQuestionId || 'default';
            const prev = this.messageControllers.get(key);
            if (prev) { try { prev.abort(); } catch (_) {} }
            const controller = new AbortController();
            this.messageControllers.set(key, controller);

            const response = await fetch(`${this.baseUrl}/chat/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
                signal: controller.signal
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Eğer backend debug bilgisi döndüyse, F12'da görebilmek için window.QUIZ_CONFIG'e yaz
                if (data?.data?.debug?.prompt_used) {
                    window.QUIZ_CONFIG = window.QUIZ_CONFIG || {};
                    window.QUIZ_CONFIG.lastAIPrompt = data.data.debug.prompt_used;
                    window.QUIZ_CONFIG.aiDebugInfo = {
                        lastPrompt: data.data.debug.prompt_used,
                        updatedAt: new Date().toISOString(),
                        type: 'message'
                    };
                    // Konsola da yaz ki F12'da net görünsün
                    // eslint-disable-next-line no-console
                    console.log('[AI Debug] Prompt used (message):', data.data.debug.prompt_used);
                }
                return {
                    success: true,
                    message: data.data.ai_response
                };
            } else {
                throw new Error(data.message || 'AI yanıtı alınamadı');
            }
        } catch (error) {
            if (error?.name === 'AbortError') {
                // eslint-disable-next-line no-console
                console.log('[AIChatService] Message request aborted');
                return { success: false, aborted: true };
            }
            console.error('[AIChatService] Send chat message error:', error);
            throw error;
        } finally {
            // Controller'ı temizle
            const k = currentQuestionId || 'default';
            const c = this.messageControllers.get(k);
            if (c && c.signal.aborted) {
                this.messageControllers.delete(k);
            }
        }
    }
    

/**
 * [6.1] getCurrentQuestionData - Mevcut sorunun verilerini alır.
 * Kategori: [6] Soru Bağlamı
 * @returns {Object|null} Soru ve şıkların içeriği
 */
getCurrentQuestionData() {
    try {
        // StateManager'dan mevcut soru bilgilerini al
        if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            const currentQuestion = state.currentQuestion;
            
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
                
                if (questionText && options.length > 0) {
                    const mappedOptions = options.map(option => ({
                        id: option.id,
                        option_text: option.text || option.option_text || option.name,
                        is_correct: option.is_correct
                    }));
                    
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
 * [3.2] isSessionActive - Chat session'ının durumunu kontrol eder.
 * Kategori: [3] Oturum
 * @returns {boolean} Session aktif mi
 */
isSessionActive() {
    return this.chatSessionId !== null;
}

/**
 * [3.3] endChatSession - Chat session'ını sonlandırır.
 * Kategori: [3] Oturum
 */
endChatSession() {
    this.chatSessionId = null;
}

/**
 * [3.4] getChatHistory - Chat history'yi getirir.
 * Kategori: [3] Oturum
 * @param {number} questionId - Soru ID
 * @returns {Promise<Object>} Chat history
 */
async getChatHistory(questionId) {
    if (!this.isEnabled) {
        console.warn('[AIChatService] Cannot get chat history - service not enabled');
        return {
            success: false,
            error: 'AI Chat service is not available'
        };
    }

    // Quiz session ID'yi window'dan al
    const quizSessionId = window.QUIZ_CONFIG?.sessionId || window.QUIZ_SESSION_ID;

    if (!quizSessionId) {
        console.error('[AIChatService] Cannot get chat history - no quiz session ID');
        return {
            success: false,
            error: 'Quiz session ID bulunamadı'
        };
    }

    // Chat session ID'yi oluştur
    const chatSessionId = `chat_${quizSessionId}_${questionId}`;

    try {
        const url = `${this.baseUrl}/chat/history?chat_session_id=${encodeURIComponent(chatSessionId)}`;

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            const messages = data.data.messages || [];
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
 * [5.1] sendQuickAction - Hızlı eylemler için AI yanıtı alır (açıkla, ipucu).
 * Kategori: [5] Hızlı Eylemler
 * @param {string} action - 'explain' veya 'hint'
 * @param {number} questionId - Soru ID
 * @param {boolean} isFirstMessage - İlk mesaj mı (soru ve şıkları eklemek için)
 * @returns {Promise<Object>} AI yanıtı
 */
async sendQuickAction(action, questionId, isFirstMessage = false) {
        
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
            }
        }
        
        // Giden quick-action isteğini konsola yaz
        // eslint-disable-next-line no-console
        console.log('[AI Debug] Sending /chat/quick-action request:', {
            ...requestBody,
            debug: (window.QUIZ_CONFIG?.aiDebug ?? true)
        });

        // Aynı soru için önceki quick-action isteğini iptal et
        const qKey = questionId || 'default';
        const prevQ = this.quickActionControllers.get(qKey);
        if (prevQ) { try { prevQ.abort(); } catch (_) {} }
        const qController = new AbortController();
        this.quickActionControllers.set(qKey, qController);

        const response = await fetch(`${this.baseUrl}/chat/quick-action`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...requestBody,
                // Debug: final prompt'u backend response'unda görmek için debug bayrağını gönder
                debug: (window.QUIZ_CONFIG?.aiDebug ?? true)
            }),
            signal: qController.signal
        });

        const data = await response.json();

        // Başarılı yanıtı işle
        if (data.status === 'success') {
            // Backend debug bilgisi döndüyse, F12'da görebilmek için window.QUIZ_CONFIG'e yaz
            if (data?.data?.debug?.prompt_used) {
                window.QUIZ_CONFIG = window.QUIZ_CONFIG || {};
                window.QUIZ_CONFIG.lastAIPrompt = data.data.debug.prompt_used;
                window.QUIZ_CONFIG.aiDebugInfo = {
                    lastPrompt: data.data.debug.prompt_used,
                    updatedAt: new Date().toISOString(),
                    type: `quick-action:${action}`
                };
                // eslint-disable-next-line no-console
                console.log('[AI Debug] Prompt used (quick-action):', data.data.debug.prompt_used);
            }
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
        if (error?.name === 'AbortError') {
            // eslint-disable-next-line no-console
            console.log('[AIChatService] Quick action request aborted');
            return { success: false, aborted: true };
        }
        console.error('[AIChatService] Quick action error:', error);
        return {
            success: false,
            error: error.message || 'Network error occurred'
        };
    } finally {
        const kq = questionId || 'default';
        const cq = this.quickActionControllers.get(kq);
        if (cq && cq.signal.aborted) {
            this.quickActionControllers.delete(kq);
        }
    }
}

/**
 * [7.1] healthCheck - Service health check yapar.
 * Kategori: [7] Sağlık
 * @returns {Promise<boolean>} Servis sağlıklı mı
 */
async healthCheck() {
    try {
        const response = await fetch(`${this.baseUrl}/system/health`);
        const data = await response.json();
        const isHealthy = data.status === 'success' && data.data.healthy;
        return isHealthy;
    } catch (error) {
        console.error('[AIChatService] Health check error:', error);
        return false;
    }
}

}

// Export for ES6 modules (default export)
/**
 * [8.1] export default - ES6 default export.
 * Kategori: [8] Dışa Aktarım
 */
export default AIChatService;

// Export for CommonJS (Node.js compatibility)
/**
 * [8.2] CommonJS export - Node.js uyumluluğu için.
 * Kategori: [8] Dışa Aktarım
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIChatService;
}