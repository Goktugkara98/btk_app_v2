/**
 * =============================================================================
 * ValidationHelpers – Doğrulama Yardımcıları | Validation Helpers
 * =============================================================================
 * Soru cevaplarının doğruluğunu kontrol etme ve anti-spam kontrollerini yönetir.
 */

export class ValidationHelpers {
    /**
     * Yerel olarak cevabın doğruluğunu kontrol eder
     */
    static checkAnswerLocally(questionId, userAnswer, questions) {
        const q = (questions || []).find(item => String(item?.question?.id) === String(questionId));
        const options = q?.question?.options || [];
        
        const correct = options.find(o => {
            if (!o) return false;
            return (o.is_correct === true || o.is_correct === 1 || o.is_correct === '1') ||
                   (o.isCorrect === true || o.isCorrect === 1 || o.isCorrect === '1') ||
                   (o.correct === true || o.correct === 1 || o.correct === '1');
        });
        
        return correct ? String(correct.id) === String(userAnswer) : false;
    }

    /**
     * Doğru cevap seçeneğini döndürür
     */
    static getCorrectAnswer(questionId, questions) {
        const q = (questions || []).find(item => String(item?.question?.id) === String(questionId));
        const options = q?.question?.options || [];
        return options.find(o => {
            if (!o) return false;
            return (o.is_correct === true || o.is_correct === 1 || o.is_correct === '1') ||
                   (o.isCorrect === true || o.isCorrect === 1 || o.isCorrect === '1') ||
                   (o.correct === true || o.correct === 1 || o.correct === '1');
        }) || null;
    }

    /**
     * Cooldown kontrolü yapar
     */
    static checkCooldown(questionId, cooldowns, cooldownMs = 4000) {
        const now = Date.now();
        const lastSent = cooldowns.get(questionId) || 0;
        return now - lastSent < cooldownMs;
    }

    /**
     * Duplicate mesaj kontrolü yapar
     */
    static isDuplicateMessage(questionId, message, lastMessageByQuestion) {
        const lastMsg = lastMessageByQuestion.get(questionId);
        return lastMsg && lastMsg === message && !message.includes('yanlış cevap verdi');
    }

    /**
     * Pending request kontrolü yapar
     */
    static hasPendingRequest(questionId, pendingRequests) {
        return pendingRequests.has(questionId);
    }

    /**
     * Session ID'yi window'dan alır
     */
    static getSessionId() {
        if (window.QUIZ_CONFIG && window.QUIZ_CONFIG.sessionId) {
            return window.QUIZ_CONFIG.sessionId;
        }
        
        if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            if (state && state.sessionId) {
                return state.sessionId;
            }
        }
        
        return null;
    }

    /**
     * Context bilgilerini state'den alır
     */
    static getContextFromState(key) {
        if (window.quizApp && window.quizApp.stateManager) {
            const state = window.quizApp.stateManager.getState();
            return state[key] || '';
        }
        return '';
    }

    /**
     * Quiz context bilgilerini hazırlar
     */
    static prepareQuizContext() {
        return {
            subject: this.getContextFromState('subject') || 'Türkçe',
            topic: this.getContextFromState('topic') || 'Sıfat-fiil',
            difficulty: this.getContextFromState('difficulty') || 'kolay'
        };
    }
}

export default ValidationHelpers;
