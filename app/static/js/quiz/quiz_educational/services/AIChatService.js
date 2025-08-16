/**
 * =============================================================================
 * AIChatService – Sohbet Servisi | Chat Service
 * =============================================================================
 * Educational quiz modunda AI tabanlı sohbet işlemlerini ve API etkileşimlerini yönetir.
 *
 * İÇİNDEKİLER | TABLE OF CONTENTS
 * 1) Çekirdek ve Kurulum | Core & Setup
 *    - constructor() - API temel yolu ve kontrol değişkenlerini başlatır.
 *    - checkServiceStatus() - Servis müsaitliğini kontrol eder ve önbelleğe alır.
 * 2) Servis Durumu | Service Status
 *    - isServiceEnabled() - Servisin etkin olup olmadığını döndürür.
 *    - healthCheck() - Altyapı sağlık kontrolü yapar.
 * 3) Oturum Yönetimi | Session Management
 *    - startChatSession(quizSessionId, questionId, context) - Sohbet oturumu başlatır/sürdürür.
 *    - isSessionActive() - Oturumun aktif olup olmadığını kontrol eder.
 *    - endChatSession() - Mevcut oturumu sonlandırır.
 *    - getChatHistory(questionId) - Soruya ait sohbet geçmişini getirir.
 * 4) Mesajlaşma | Messaging
 *    - sendChatMessage(message, currentQuestionId, isFirstMessage) - Sohbet mesajı gönderir.
 * 5) Hızlı Eylemler | Quick Actions
 *    - sendQuickAction(action, questionId, isFirstMessage) - Hızlı eylem gönderir.
 * 6) Soru Bağlamı | Question Context
 *    - getCurrentQuestionData() - Sorunun metin ve seçeneklerini döndürür.
 * 7) Dışa Aktarım | Export
 * =============================================================================
 */
class AIChatService {

    /* =========================================================================
     * 1) Çekirdek ve Kurulum | Core & Setup
     * ========================================================================= */

    /**
     * Servis ayarlarını başlatır, API adresini tanımlar ve servisin kullanılabilirliğini kontrol eder.
     */
    constructor() {
      this.baseUrl = '/api/ai';
      this.isEnabled = false;
      this.chatSessionId = null;

      // Eşzamanlı API çağrılarını yönetmek ve iptal edebilmek için AbortController'lar.
      this.messageControllers = new Map();
      this.quickActionControllers = new Map();
      
      this.checkServiceStatus();
    }

    /**
     * Başlangıçta ve periyodik olarak AI servisinin genel durumunu (aktif/pasif) sunucudan kontrol eder.
     */
    async checkServiceStatus() {
      try {
        const response = await fetch(`${this.baseUrl}/system/status`);
        const data = await response.json();
        this.isEnabled = data?.status === 'success' && data?.data?.available;
      } catch (error) {
        console.error('[AIChatService] Status check error:', error);
        this.isEnabled = false;
      }
    }

    /* =========================================================================
     * 2) Servis Durumu | Service Status
     * ========================================================================= */

    /**
     * AI servisinin o an kullanılabilir olup olmadığını döndürür.
     * @returns {boolean} Servis etkinse true, değilse false.
     */
    isServiceEnabled() {
      return this.isEnabled;
    }
    
    /**
     * AI servisinin altyapısının sağlıklı çalışıp çalışmadığını kontrol eder.
     * @returns {Promise<boolean>} Servis sağlıklı ise true döner.
     */
    async healthCheck() {
      try {
        const response = await fetch(`${this.baseUrl}/system/health`);
        const data = await response.json();
        return data.status === 'success' && data.data.healthy;
      } catch (error) {
        console.error('[AIChatService] Health check error:', error);
        return false;
      }
    }

    /* =========================================================================
     * 3) Oturum Yönetimi | Session Management
     * ========================================================================= */

    /**
     * Belirli bir soru için yeni bir sohbet oturumu başlatır veya mevcut olanı devam ettirir.
     * @param {string} quizSessionId - Ana quiz oturumunun kimliği.
     * @param {number} questionId - Sohbetin ilişkilendirileceği soru kimliği.
     * @param {Object} context - Oturumla ilgili ek bağlam bilgileri.
     * @returns {Promise<Object>} Başarılı ise oturum bilgilerini içeren nesne.
     */
    async startChatSession(quizSessionId, questionId, context = {}) {
      if (!this.isEnabled) {
        return { success: false, error: 'AI Chat service is not available' };
      }

      try {
        // Her soru için benzersiz chat session ID oluştur
        const chatSessionId = `chat_${quizSessionId}_${questionId}`;
        
        // Önceki soru için bekleyen request'leri temizle
        this.messageControllers.forEach((controller, key) => {
          if (key !== questionId) {
            controller.abort();
            this.messageControllers.delete(key);
          }
        });
        
        this.quickActionControllers.forEach((controller, key) => {
          if (key !== questionId) {
            controller.abort();
            this.quickActionControllers.delete(key);
          }
        });
        
        const response = await fetch(`${this.baseUrl}/session/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            quiz_session_id: quizSessionId,
            question_id: questionId,
            chat_session_id: chatSessionId,
            context: context
          })
        });

        const data = await response.json();
        if (data.status === 'success') {
          this.chatSessionId = data?.data?.chat_session_id || chatSessionId;
          return { success: true, chatSessionId: this.chatSessionId };
        } else {
          throw new Error(data.message || 'Failed to start chat session');
        }
      } catch (error) {
        console.error('[AIChatService] Start chat session error:', error);
        return { success: false, error: error.message };
      }
    }

    /**
     * Aktif bir sohbet oturumunun olup olmadığını kontrol eder.
     * @returns {boolean} Oturum aktifse true.
     */
    isSessionActive() {
      return this.chatSessionId !== null;
    }

    /**
     * Mevcut sohbet oturumunu sonlandırır ve session ID'yi temizler.
     */
    endChatSession() {
      this.chatSessionId = null;
    }

    /**
     * Belirli bir soruya ait sohbet geçmişini sunucudan getirir.
     * @param {number} questionId - Geçmişi alınacak sorunun kimliği.
     * @returns {Promise<Object>} Başarılı ise mesaj listesini içeren nesne.
     */
    async getChatHistory(questionId) {
      if (!this.isEnabled) {
        return { success: false, error: 'AI Chat service is not available' };
      }
      const quizSessionId = window.QUIZ_CONFIG?.sessionId || window.QUIZ_SESSION_ID;
      if (!quizSessionId) {
        return { success: false, error: 'Quiz session ID not found' };
      }

      const chatSessionId = `chat_${quizSessionId}_${questionId}`;
      try {
        const url = `${this.baseUrl}/chat/history?chat_session_id=${encodeURIComponent(chatSessionId)}`;
        const response = await fetch(url);
        const data = await response.json();

        if (data.status === 'success') {
          return { success: true, messages: data.data.messages || [] };
        } else {
          throw new Error(data.message || 'Failed to get chat history');
        }
      } catch (error) {
        console.error('[AIChatService] Get chat history error:', error);
        return { success: false, error: error.message };
      }
    }

    /* =========================================================================
     * 4) Mesajlaşma | Messaging
     * ========================================================================= */

    /**
     * Kullanıcının yazdığı bir mesajı AI servisine gönderir ve yanıtını alır.
     * @param {Object} messageData - Mesaj verisi paketi
     * @param {string} messageData.message - Kullanıcının gönderdiği metin mesajı
     * @param {number} messageData.questionId - Mesajın ilgili olduğu soru kimliği
     * @param {boolean} messageData.isFirstMessage - Bu mesajın o soru için ilk mesaj olup olmadığı
     * @param {('direct'|'wrong_answer'|'quick_action')} messageData.scenarioType - Mesaj senaryosu
     * @param {Object} messageData.questionContext - Soru bilgileri (text, options)
     * @param {Object} messageData.userAction - Kullanıcı aksiyonu detayları
     * @returns {Promise<Object>} Başarılı ise AI yanıtını içeren nesne.
     */
    async sendChatMessage(messageData) {
      // Mesaj verilerini çıkar
      const {
        message,
        questionId = null,
        isFirstMessage = false,
        scenarioType = 'direct',
        questionContext = null,
        userAction = {}
      } = messageData;

      if (!this.isEnabled || !this.chatSessionId) {
        throw new Error('AI Chat service is not available or session not started.');
      }
      if (!message || !message.trim()) {
        throw new Error('Message cannot be empty.');
      }

      const key = questionId || 'default';
      const prevController = this.messageControllers.get(key);
      if (prevController) {
        prevController.abort();
      }
      const controller = new AbortController();
      this.messageControllers.set(key, controller);
      
      try {
        // Gelişmiş request body oluştur
        const requestBody = {
          message: message.trim(),
          chat_session_id: this.chatSessionId,
          question_id: questionId,
          is_first_message: !!isFirstMessage,
          scenario_type: scenarioType,
          user_action: {
            type: userAction.type || 'direct_message', // 'direct_message', 'wrong_answer', 'quick_action'
            trigger: userAction.trigger || 'user_input', // 'user_input', 'auto_trigger', 'button_click'
            context: userAction.context || {} // Ek bağlam bilgileri
          },
          debug: window.QUIZ_CONFIG?.aiDebug ?? true
        };

        // Soru bağlamını ekle (her zaman, sadece ilk mesajda değil)
        if (questionContext || (questionId && this.getCurrentQuestionData())) {
          requestBody.question_context = questionContext || this.getCurrentQuestionData();
        }

        // Debug: Log the exact outgoing request payload to the console (F12)
        if (window?.QUIZ_CONFIG?.debug || window?.QUIZ_CONFIG?.aiDebug) {
          const debugLog = {
            url: `${this.baseUrl}/chat/message`,
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: requestBody,
            bodyString: JSON.stringify(requestBody)
          };
          // Use warn to keep alignment with previous no-console.log policy
          console.warn('[AIChatService] Outgoing AI message payload', debugLog);
          window.__LAST_AI_REQUEST__ = {
            timestamp: new Date().toISOString(),
            ...debugLog
          };
        }

        const response = await fetch(`${this.baseUrl}/chat/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
          signal: controller.signal
        });

        const data = await response.json();
        
        if (data.status === 'success') {
          // Debug: Log server-side final prompt if provided
          if (window?.QUIZ_CONFIG?.debug || window?.QUIZ_CONFIG?.aiDebug) {
            const promptUsed = data?.data?.debug?.prompt_used;
            if (promptUsed) {
              console.warn('[AIChatService] Server prompt_used (message)', {
                prompt: promptUsed,
                chat_session_id: data?.data?.chat_session_id
              });
              window.__LAST_AI_PROMPT__ = {
                timestamp: new Date().toISOString(),
                source: 'message',
                chat_session_id: data?.data?.chat_session_id,
                prompt: promptUsed
              };
            }
          }
          return { success: true, message: data.data.ai_response };
        } else {
          throw new Error(data.message || 'Failed to get AI response');
        }
      } catch (error) {
        if (error?.name === 'AbortError') {
          return { success: false, aborted: true, message: 'Request was aborted.' };
        }
        console.error('[AIChatService] Send chat message error:', error);
        throw error;
      } finally {
        this.messageControllers.delete(key);
      }
    }
    
    /* =========================================================================
     * 5) Hızlı Eylemler | Quick Actions
     * ========================================================================= */

    /**
     * Önceden tanımlanmış eylemi AI servisine gönderir.
     * @param {Object} actionData - Eylem verisi paketi
     * @param {string} actionData.action - Gerçekleştirilecek eylemin adı ('explain')
     * @param {number} actionData.questionId - Eylemin ilgili olduğu soru kimliği
     * @param {boolean} actionData.isFirstMessage - Bu eylemin o soru için ilk etkileşim olup olmadığı
     * @param {Object} actionData.questionContext - Soru bilgileri
     * @param {Object} actionData.userAction - Kullanıcı aksiyonu detayları
     * @returns {Promise<Object>} Başarılı ise AI yanıtını içeren nesne.
     */
    async sendQuickAction(actionData) {
      // Eylem verilerini çıkar
      const {
        action,
        questionId = null,
        isFirstMessage = false,
        questionContext = null,
        userAction = {}
      } = actionData;

      if (!this.isEnabled || !this.chatSessionId) {
        return { success: false, error: 'AI Chat service is not available or session not started.' };
      }

      const key = questionId || 'default';
      const prevController = this.quickActionControllers.get(key);
      if (prevController) {
        prevController.abort();
      }
      const controller = new AbortController();
      this.quickActionControllers.set(key, controller);

      try {
        // Gelişmiş request body oluştur
        const requestBody = {
          action,
          chat_session_id: this.chatSessionId,
          question_id: questionId,
          is_first_message: !!isFirstMessage,
          scenario_type: 'quick_action',
          user_action: {
            type: 'quick_action',
            trigger: 'button_click',
            action_name: action,
            context: userAction.context || {}
          },
          debug: window.QUIZ_CONFIG?.aiDebug ?? true
        };

        // Soru bağlamını ekle (her zaman)
        if (questionContext || (questionId && this.getCurrentQuestionData())) {
          requestBody.question_context = questionContext || this.getCurrentQuestionData();
        }

        // Debug: Log the exact outgoing quick-action request payload
        if (window?.QUIZ_CONFIG?.debug || window?.QUIZ_CONFIG?.aiDebug) {
          const debugLog = {
            url: `${this.baseUrl}/chat/quick-action`,
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: requestBody,
            bodyString: JSON.stringify(requestBody)
          };
          console.warn('[AIChatService] Outgoing AI quick-action payload', debugLog);
          window.__LAST_AI_REQUEST__ = {
            timestamp: new Date().toISOString(),
            ...debugLog
          };
        }

        const response = await fetch(`${this.baseUrl}/chat/quick-action`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
          signal: controller.signal
        });

        const data = await response.json();

        if (data.status === 'success') {
          // Debug: Log server-side final prompt if provided
          if (window?.QUIZ_CONFIG?.debug || window?.QUIZ_CONFIG?.aiDebug) {
            const promptUsed = data?.data?.debug?.prompt_used;
            if (promptUsed) {
              console.warn('[AIChatService] Server prompt_used (quick-action)', {
                prompt: promptUsed,
                chat_session_id: data?.data?.chat_session_id,
                action,
                question_id: questionId
              });
              window.__LAST_AI_PROMPT__ = {
                timestamp: new Date().toISOString(),
                source: 'quick-action',
                chat_session_id: data?.data?.chat_session_id,
                action,
                question_id: questionId,
                prompt: promptUsed
              };
            }
          }
          return { success: true, message: data.data.ai_response, action };
        } else {
          throw new Error(data.message || 'Quick action failed');
        }
      } catch (error) {
         if (error?.name === 'AbortError') {
          return { success: false, aborted: true, error: 'Request was aborted.' };
        }
        console.error('[AIChatService] Quick action error:', error);
        return { success: false, error: error.message };
      } finally {
        this.quickActionControllers.delete(key);
      }
    }

    /* =========================================================================
     * 6) Soru Bağlamı | Question Context
     * ========================================================================= */
 
     /**
      * StateManager üzerinden mevcut aktif sorunun metnini ve seçeneklerini alır.
      * Bu veri, AI'a bağlam sağlamak için kullanılır.
      * @returns {Object|null} Soru metni ve seçenekleri içeren nesne veya null.
      */
      getCurrentQuestionData() {
        try {
          if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            const currentQuestion = (state?.questions && state.questions.length > 0)
              ? state.questions[state.currentQuestionIndex]
              : null;
            
            if (currentQuestion?.question) {
              const questionText = (
                currentQuestion.question.text ??
                currentQuestion.question.name ??
                currentQuestion.question.title ??
                currentQuestion.text ??
                currentQuestion.name ??
                ''
              );
              const options = currentQuestion.question.options || [];
  
              if (questionText && options.length > 0) {
                return {
                  question_text: String(questionText),
                  options: options.map(opt => {
                    const id = (opt && (opt.id ?? opt.option_id ?? opt.value ?? null));
                    const text = (opt && (
                      opt.text ?? opt.name ?? opt.title ?? opt.option_text ?? opt.label ?? opt.description ?? opt.content ?? (typeof opt.value !== 'object' ? opt.value : '') ?? ''
                    ));
                    const isCorrectRaw = (opt?.is_correct ?? opt?.isCorrect ?? opt?.correct);
                    const is_correct = (isCorrectRaw === true || isCorrectRaw === 1 || isCorrectRaw === '1');
                    return { id, option_text: String(text || ''), is_correct };
                  })
                };
              }
            }
          }
          return null;
        } catch (error) {
          console.error('[AIChatService] Error getting current question data:', error);
          return null;
        }
      }
 
   }
 
   /* =========================================================================
    * 7) Dışa Aktarım | Export
    * ========================================================================= */
 
   // ES6 modül sistemi için varsayılan dışa aktarım.
   export default AIChatService;
 
   // Node.js gibi CommonJS ortamlarıyla uyumluluk için ek dışa aktarım.
   if (typeof module !== 'undefined' && module.exports) {
     module.exports = AIChatService;
   }