/**
 * demo-simulation.js
 * Sadece index sayfasındaki demo quiz ve AI chat panelini yönetir.
 * Hiçbir şekilde hero kodu veya dosyası ile bağlantılı değildir.
 * Modüler, sade, kolay genişletilebilir yapı.
 */

export function initIndexDemoSimulation() {
    console.log('🔍 Index Demo Simulation başlatılıyor...');
    
    // Auto-follow mode state
    let autoFollowMode = true;
    let scrollButton = null;
    
    // Check if elements exist
    const questionElement = document.getElementById('index-demo-question');
    const optionsContainer = document.getElementById('index-demo-options');
    const chatMessages = document.getElementById('index-demo-chat-messages');
    scrollButton = document.getElementById('index-demo-scroll-to-bottom');
    
    console.log('📋 Elementler:', {
        question: questionElement,
        options: optionsContainer,
        chat: chatMessages,
        scrollButton: scrollButton
    });
    
    if (!questionElement || !optionsContainer || !chatMessages) {
        console.error('❌ Gerekli elementler bulunamadı!');
        return;
    }

    // Initialize scroll button functionality
    if (scrollButton) {
        scrollButton.addEventListener('click', () => {
            scrollToBottomAndFollow(chatMessages);
        });
    }

    // Listen for scroll events to disable auto-follow when user scrolls up
    let scrollTimeout;
    chatMessages.addEventListener('scroll', () => {
        const isAtBottom = chatMessages.scrollTop + chatMessages.clientHeight >= chatMessages.scrollHeight - 10;
        
        if (!isAtBottom && autoFollowMode) {
            autoFollowMode = false;
            console.log('🔕 Auto-follow mode disabled (user scrolled up)');
        } else if (isAtBottom && !autoFollowMode) {
            autoFollowMode = true;
            console.log('🔔 Auto-follow mode enabled (user at bottom)');
        }
        
        // Debounce button visibility update to prevent flashing
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            updateScrollButtonVisibility(chatMessages);
        }, 150);
    });
    
    // Global variables for scenarios data
    let scenariosData = null;
    let currentScenarioIndex = 0;

    // Load and play sequential scenario
    loadSequentialScenario();

    // Load only science scenario (photosynthesis)
    async function loadSequentialScenario() {
        try {
            // Load scenarios data only once
            if (!scenariosData) {
                const response = await fetch('/app/data/demo-scenarios.json');
                scenariosData = await response.json();
            }
            
            // Get current scenario
            const scenario = scenariosData.scenarios[currentScenarioIndex];
            
            // Load scenario into UI
            loadScenarioToUI(scenario);
            
            // Start playing the scenario
            playScenario(scenario, onScenarioEnd);
            
        } catch (error) {
            console.error('Error loading scenarios:', error);
            // Fallback to default scenario
            loadDefaultScenario();
        }
    }

    function onScenarioEnd() {
        // Bir sonraki senaryoya geç
        currentScenarioIndex = (currentScenarioIndex + 1) % scenariosData.scenarios.length;
        setTimeout(loadSequentialScenario, 1000); // 1 saniye bekle
    }

    // Load scenario data into UI
    function loadScenarioToUI(scenario) {
        console.log('Loading scenario:', scenario); // Debug log
        
        // Update question
        const questionElement = document.getElementById('index-demo-question');
        if (questionElement) {
            questionElement.textContent = scenario.question;
            console.log('Updated question:', scenario.question); // Debug log
        } else {
            console.error('Question element not found!'); // Debug log
        }
        
        // Update subject and difficulty
        const subjectElement = document.querySelector('.index-demo-quiz-meta .index-demo-quiz-subject');
        const difficultyElement = document.querySelector('.index-demo-quiz-meta .index-demo-quiz-difficulty');
        if (subjectElement) {
            subjectElement.textContent = scenario.subject;
            console.log('Updated subject:', scenario.subject); // Debug log
        }
        if (difficultyElement) {
            difficultyElement.textContent = scenario.difficulty;
            console.log('Updated difficulty:', scenario.difficulty); // Debug log
        }
        
        // Update options
        const optionsContainer = document.getElementById('index-demo-options');
        if (optionsContainer) {
            optionsContainer.innerHTML = '';
            scenario.options.forEach(option => {
                const optionElement = document.createElement('div');
                optionElement.className = 'index-demo-option';
                optionElement.setAttribute('data-correct', option.correct ? 'true' : 'false');
                optionElement.innerHTML = `
                    <span class="index-demo-option-letter">${option.letter}</span>
                    <span class="index-demo-option-text">${option.text}</span>
                `;
                optionsContainer.appendChild(optionElement);
            });
            console.log('Updated options:', scenario.options); // Debug log
        } else {
            console.error('Options container not found!'); // Debug log
        }
    }

    // Play scenario steps sequentially
    function playScenario(scenario, onComplete) {
        const options = document.querySelectorAll('.index-demo-option');
        const chatMessages = document.getElementById('index-demo-chat-messages');
        
        // Disable manual clicking
        options.forEach(option => {
            option.style.pointerEvents = 'none';
        });
        
        // Clear chat
        chatMessages.innerHTML = '';
        
        // Play scenario steps sequentially
        let step = 0;
        function playNextStep() {
            if (step < scenario.steps.length) {
                const currentStep = scenario.steps[step];
                setTimeout(() => {
                    executeStep(currentStep, () => {
                        // Callback when step is complete
                        step++;
                        playNextStep();
                    });
                }, currentStep.delay);
            } else {
                // Senaryo bittiğinde onComplete çağır
                if (onComplete) onComplete();
            }
        }
        playNextStep();
    }

    // Execute a single step
    function executeStep(step, callback) {
        switch (step.type) {
            case 'ai':
                addChatMessage(step.message, 'ai', callback);
                break;
            case 'user':
                addChatMessage(step.message, 'user', callback);
                break;
            case 'select':
                const selectedText = selectOption(step.option);
                if (selectedText) {
                    addChatMessage(selectedText, 'user', () => {
                        // After user message is added, call the callback
                        if (callback) setTimeout(callback, 100);
                    });
                } else {
                    // Fallback if no text found
                    if (callback) setTimeout(callback, 300);
                }
                break;
        }
    }

    // Select option with visual feedback
    function selectOption(letter) {
        const options = document.querySelectorAll('.index-demo-option');
        const selectedOption = Array.from(options).find(option => 
            option.querySelector('.index-demo-option-letter').textContent === letter
        );
        
        if (selectedOption) {
            // Clear previous selections
            options.forEach(opt => {
                opt.classList.remove('selected', 'correct', 'incorrect');
            });
            
            // Mark selected option
            selectedOption.classList.add('selected');
            
            const isCorrect = selectedOption.getAttribute('data-correct') === 'true';
            
            if (isCorrect) {
                selectedOption.classList.add('correct');
            } else {
                selectedOption.classList.add('incorrect');
            }
            
            // Get the text content of the selected option
            const selectedText = selectedOption.querySelector('.index-demo-option-text').textContent;
            return selectedText; // Return the selected text
        }
        return null;
    }

    // Smart scroll function - only scroll if auto-follow mode is active
    function smartScrollToBottom(chatMessages) {
        if (autoFollowMode) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Check if user is at bottom and update button visibility
    function updateScrollButtonVisibility(chatMessages) {
        if (!scrollButton) return;
        
        const isAtBottom = chatMessages.scrollTop + chatMessages.clientHeight >= chatMessages.scrollHeight - 10;
        
        if (isAtBottom) {
            scrollButton.classList.remove('active');
        } else {
            scrollButton.classList.add('active');
        }
    }

    // Scroll to bottom and enable auto-follow
    function scrollToBottomAndFollow(chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
        autoFollowMode = true;
        updateScrollButtonVisibility(chatMessages);
    }

    // Add chat message with typing effect
    function addChatMessage(text, type = 'ai', callback = null) {
        console.log(`💬 Mesaj ekleniyor: "${text}" (${type})`);
        
        const chatMessages = document.getElementById('index-demo-chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `index-demo-message index-demo-${type}-message`;
        
        console.log(`🎨 CSS class: ${messageDiv.className}`);
        
        if (type === 'ai') {
            // AI message with typing effect only
            messageDiv.classList.add('typing');
            messageDiv.innerHTML = '<p></p>';
            chatMessages.appendChild(messageDiv);
            
            const p = messageDiv.querySelector('p');
            
            // Split text into lines for better control
            const lines = text.split('\n');
            let currentLine = 0;
            let currentChar = 0;
            let displayText = '';
            
            const typeWriter = () => {
                if (currentLine < lines.length) {
                    const line = lines[currentLine];
                    
                    if (currentChar < line.length) {
                        // Add character to current line
                        displayText += line.charAt(currentChar);
                        currentChar++;
                    } else {
                        // Move to next line
                        displayText += '\n';
                        currentLine++;
                        currentChar = 0;
                    }
                    
                    // Update display with proper line breaks
                    p.innerHTML = displayText.replace(/\n/g, '<br>');
                    
                    // Smart scroll - only if user is at bottom
                    smartScrollToBottom(chatMessages);
                    
                    // Continue typing with faster speed
                    setTimeout(typeWriter, 25); // Faster typing speed
                } else {
                    // Remove typing class when done
                    messageDiv.classList.remove('typing');
                    
                    // Smart scroll after typing is complete
                    smartScrollToBottom(chatMessages);
                    
                    // Update button visibility after typing is complete
                    setTimeout(() => {
                        updateScrollButtonVisibility(chatMessages);
                    }, 100);
                    
                    // Call callback when typing is complete
                    if (callback) {
                        setTimeout(callback, 100); // Shorter delay
                    }
                }
            };
            typeWriter();
        } else {
            // User message (instant)
            messageDiv.innerHTML = `<p>${text}</p>`;
            chatMessages.appendChild(messageDiv);
            // Smart scroll - only if user is at bottom
            smartScrollToBottom(chatMessages);
            
            // Update button visibility after a short delay
            setTimeout(() => {
                updateScrollButtonVisibility(chatMessages);
            }, 100);
            
            // Call callback immediately for user messages
            if (callback) {
                setTimeout(callback, 50); // Shorter delay
            }
        }
        
        // Additional smart scroll after a short delay to ensure it works
        setTimeout(() => {
            smartScrollToBottom(chatMessages);
        }, 50);
    }

    // Fallback default scenario
    function loadDefaultScenario() {
        const defaultScenario = {
            question: "Aşağıdaki sayılardan hangisi en büyüktür?",
            subject: "Matematik",
            difficulty: "Orta",
            options: [
                { letter: "A", text: "1250", correct: true },
                { letter: "B", text: "999", correct: false },
                { letter: "C", text: "850", correct: false },
                { letter: "D", text: "750", correct: false }
            ],
            steps: [
                { delay: 500, type: "ai", message: "Merhaba! Bu soruyu birlikte çözelim." },
                { delay: 1000, type: "select", option: "B" },
                { delay: 800, type: "ai", message: "999'u seçmişsin... Bu sayıyı seçmenin mantıklı bir sebebi var mı?" },
                { delay: 1200, type: "ai", message: "Aslında 1250 daha büyük bir sayı. 999'u seçmenin sebebi ne olabilir?" },
                { delay: 800, type: "select", option: "A" },
                { delay: 800, type: "ai", message: "Mükemmel! 1250 doğru cevap. Neden bu sefer doğru düşündün?" }
            ]
        };
        
        loadScenarioToUI(defaultScenario);
        setTimeout(() => playScenario(defaultScenario), 300);
    }
} 