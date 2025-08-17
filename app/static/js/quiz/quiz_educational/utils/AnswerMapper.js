/**
 * =============================================================================
 * AnswerMapper – Cevap Eşleştirici | Answer Mapper Utility
 * =============================================================================
 * Soru cevaplarını ID'den metne çevirme işlemlerini merkezi olarak yönetir.
 * Kod tekrarını önler ve tutarlılık sağlar.
 */

export class AnswerMapper {
    /**
     * Answer ID'lerini option text'lerine çevirir
     * @param {string|number} userAnswer - Kullanıcının cevap ID'si
     * @param {string|number|Object} correctAnswer - Doğru cevap ID'si veya nesnesi
     * @param {Array} options - Soru seçenekleri
     * @returns {Object} {userAnswerText, correctAnswerText}
     */
    static mapAnswerIdsToTexts(userAnswer, correctAnswer, options = []) {
        let userAnswerText = userAnswer;
        let correctAnswerText = correctAnswer?.id || correctAnswer;
        
        try {
            // Kullanıcı cevabını metne çevir
            const userOpt = options.find(o => String(o.id) === String(userAnswer));
            if (userOpt) userAnswerText = userOpt.option_text || userOpt.name || userOpt.text;
            
            // Doğru cevabı metne çevir
            const correctId = (correctAnswer && typeof correctAnswer === 'object') 
                ? correctAnswer.id 
                : correctAnswer;
            const correctOpt = options.find(o => String(o.id) === String(correctId));
            if (correctOpt) correctAnswerText = correctOpt.option_text || correctOpt.name || correctOpt.text;
            
        } catch (error) {
            console.warn('[AnswerMapper] Could not map answer IDs to texts:', error);
        }
        
        return { userAnswerText, correctAnswerText };
    }
    
}

export default AnswerMapper;
