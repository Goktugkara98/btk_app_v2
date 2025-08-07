// =============================================================================
// LOGIN/REGISTER AI CHAT PANEL SECTION JS
// =============================================================================

function createMessageElement(content, type = 'ai') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content;
    messageDiv.appendChild(contentDiv);
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = 'Şimdi';
    messageDiv.appendChild(timeDiv);
    return messageDiv;
}

function handleChat(panelIdPrefix) {
    const messages = document.getElementById(`${panelIdPrefix}-chat-messages`);
    const input = document.getElementById(`${panelIdPrefix}-chat-input`);
    const sendBtn = document.getElementById(`${panelIdPrefix}-send-message`);

    function sendUserMessage() {
        const text = input.value.trim();
        if (!text) return;
        messages.appendChild(createMessageElement(text, 'user'));
        input.value = '';
        messages.scrollTop = messages.scrollHeight;
        setTimeout(() => {
            // Simple demo AI response
            let aiReply = 'Sorunu aldım! Şu an için temel bir demo yanıtı veriyorum.';
            if (text.toLowerCase().includes('şifre')) aiReply = 'Şifreni unuttuysan, "Şifremi unuttum" linkini kullanabilirsin.';
            if (text.toLowerCase().includes('kayıt')) aiReply = 'Kayıt olurken e-posta adresinin doğru olduğundan emin ol.';
            messages.appendChild(createMessageElement(aiReply, 'ai'));
            messages.scrollTop = messages.scrollHeight;
        }, 700);
    }

    sendBtn.addEventListener('click', sendUserMessage);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            sendUserMessage();
        }
    });
}

export function initLoginInfo() {
    // For login page
    if (document.getElementById('login-chat-messages')) {
        handleChat('login');
    }
    // For register page
    if (document.getElementById('register-chat-messages')) {
        handleChat('register');
    }
} 