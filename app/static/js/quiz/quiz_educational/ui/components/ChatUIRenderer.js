/**
 * =============================================================================
 * ChatUIRenderer – Sohbet UI Oluşturucu | Chat UI Renderer
 * =============================================================================
 * Chat arayüzü render işlemlerini yönetir (mesaj ekleme, typing, status vb.)
 */

export class ChatUIRenderer {
    constructor(elements) {
        this.messagesContainer = elements.messagesContainer;
        this.inputField = elements.inputField;
        this.sendButton = elements.sendButton;
        this.quickActionButtons = elements.quickActionButtons;
    }

    /**
     * Mesaj ekler
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
            
            const textElement = messageDiv.querySelector('.ai-message-text');
            if (isFromHistory) {
                textElement.innerHTML = this.formatMessage(content);
            } else {
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
     * Typewriter efekti
     */
    typewriterEffect(element, text, speed = 15) {
        let index = 0;
        
        const typeInterval = setInterval(() => {
            if (index < text.length) {
                element.innerHTML = text.substring(0, index + 1);
                index++;
                this.scrollToBottom();
            } else {
                this.updateAIStatus('online', 'Çevrimiçi');
                clearInterval(typeInterval);
            }
        }, speed);
    }

    /**
     * Typing göstergesi
     */
    showTyping() {
        if (document.querySelector('.typing-indicator')) {
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
     * AI status günceller
     */
    updateAIStatus(status, text) {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-text');
        
        if (statusIndicator && statusText) {
            statusIndicator.className = 'status-indicator';
            statusIndicator.classList.add(status);
            statusText.textContent = text;
        }
    }

    /**
     * Mesaj formatlar
     */
    formatMessage(message) {
        return message
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    /**
     * Chat temizler
     */
    clearChat() {
        if (this.messagesContainer) {
            this.messagesContainer.innerHTML = '';
        }
    }
    
    /**
     * Scroll to bottom
     */
    scrollToBottom() {
        if (this.messagesContainer) {
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
     * Input alanını otomatik boyutlandırır
     */
    autoResizeTextarea() {
        if (this.inputField) {
            this.inputField.style.height = 'auto';
            this.inputField.style.height = Math.min(this.inputField.scrollHeight, 120) + 'px';
        }
    }

    /**
     * Chat kontrollerini aktif/pasif yapar
     */
    toggleChatControls(enabled) {
        if (this.inputField) {
            this.inputField.disabled = !enabled;
            this.inputField.placeholder = enabled 
                ? "Daima'ya soru sor veya yardım iste..."
                : "AI sohbet servisi kullanılamıyor...";
        }
        
        if (this.sendButton) {
            this.sendButton.disabled = !enabled;
        }
        
        if (this.quickActionButtons && this.quickActionButtons.length > 0) {
            this.quickActionButtons.forEach(button => {
                button.disabled = !enabled;
            });
        }
    }

    /**
     * Hoş geldin mesajı gösterir
     */
    showWelcomeMessage() {
        this.addMessage('ai', 'Merhaba! Ben Daima, senin AI öğretmenin! Sorularınla ilgili yardıma ihtiyacın var mı? 🤖✨');
    }
}

export default ChatUIRenderer;
