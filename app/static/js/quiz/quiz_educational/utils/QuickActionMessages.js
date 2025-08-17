/**
 * =============================================================================
 * QuickActionMessages – Hızlı Eylem Mesajları | Quick Action Messages
 * =============================================================================
 * Her hızlı eylem için özel kullanıcı mesajları ve etiketleri sağlar.
 */

export class QuickActionMessages {
    /**
     * Hızlı eylem türüne göre kullanıcı mesajını döndürür
     * @param {string} action - Eylem türü
     * @returns {string} Kullanıcı mesajı
     */
    static getUserMessage(action) {
        const messages = {
            'explain': 'Bu soruyu detaylı bir şekilde açıklar mısın? Konuyu tam olarak anlayamadım.',
            'give_hint': 'Bu soru için bana bir ipucu verebilir misin? Hangi yöne odaklanmalıyım?',
            'how_to_solve': 'Bu tür soruları nasıl çözmeliyim? Yaklaşım stratejimi öğretir misin?',
            'eliminate_options': 'Hangi şıkları elemeli ve neden? Mantıklı bir eleme süreci yapalım.',
            'solve_step_by_step': 'Bu soruyu adım adım çözelim. Her aşamayı detaylı anlat.'
        };
        
        return messages[action] || `${action} hakkında yardım istiyorum.`;
    }
    
    /**
     * Hızlı eylem türüne göre etiket döndürür
     * @param {string} action - Eylem türü
     * @returns {string} Eylem etiketi
     */
    static getActionLabel(action) {
        const labels = {
            'explain': 'Soru Açıklaması',
            'give_hint': 'İpucu Talebi',
            'how_to_solve': 'Çözüm Stratejisi',
            'eliminate_options': 'Şık Eleme',
            'solve_step_by_step': 'Adım Adım Çözüm'
        };
        
        return labels[action] || 'Hızlı Eylem';
    }
    
    /**
     * Tüm desteklenen eylemleri döndürür
     * @returns {Array<string>} Desteklenen eylem listesi
     */
    static getSupportedActions() {
        return ['explain', 'give_hint', 'how_to_solve', 'eliminate_options', 'solve_step_by_step'];
    }
    
    /**
     * Eylemin geçerli olup olmadığını kontrol eder
     * @param {string} action - Kontrol edilecek eylem
     * @returns {boolean} Geçerli ise true
     */
    static isValidAction(action) {
        return this.getSupportedActions().includes(action);
    }
}

export default QuickActionMessages;
