/**
 * HERO SECTION JAVASCRIPT
 * 
 * Kullanıcı etkileşimli quiz simülasyonu için modern ve yeniden düzenlenmiş JavaScript kodu.
 * Bu sürüm, daha iyi okunabilirlik, performans ve yönetilebilirlik için
 * olay delegasyonu (event delegation), öğe önbellekleme (element caching) ve
 * daha temiz bir mantık akışı kullanır.
 * =============================================================================
 */

// Hero Quiz Module
export function initHeroQuiz() {
    // Soruları dışarıdan yükle
    fetch('/app/data/hero-questions.json')
        .then(res => res.json())
        .then(data => {
            new HeroQuiz(data);
        })
        .catch((error) => {
            const quizPanel = document.querySelector('.quiz-panel .rotate-inner') || document.querySelector('.quiz-panel');
            if (quizPanel) quizPanel.innerHTML = '<div style="padding:2rem; color:red;">Soru verisi yüklenemedi.</div>';
        });

    class HeroQuiz {
        constructor(questions) {
            // Soruları karıştır
            this.questions = this.shuffleArray(questions);

            // DOM elements
            this.elements = {
                question: document.getElementById('demo-question'),
                optionsContainer: document.getElementById('demo-options'),
                quizInfo: document.querySelector('.quiz-info'),
                chatMessages: document.getElementById('chat-messages'),
            };

            // Quiz state
            this.currentQuestionIndex = 0;
            this.isAnswered = false;
            this.timerDuration = 20; // 20 saniye
            this.timer = null;
            this.timeLeft = this.timerDuration;

            this.init();
        }

        shuffleArray(array) {
            // Fisher-Yates algoritması
            const arr = array.slice();
            for (let i = arr.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [arr[i], arr[j]] = [arr[j], arr[i]];
            }
            return arr;
        }

        /**
         * Quiz'i başlatan ana fonksiyon
         */
        init() {
            this.bindEvents();
            this.loadQuestion();
        }

        /**
         * Olay dinleyicilerini bağla
         */
        bindEvents() {
            // Seçeneklere tıklamayı yönetmek için olay delegasyonu kullanalım.
            // Bu, her seçenek için ayrı bir dinleyici eklemekten daha verimlidir.
            this.elements.optionsContainer.addEventListener('click', (event) => {
                const selectedOption = event.target.closest('.option');
                if (selectedOption && !this.isAnswered) {
                    this.handleAnswer(selectedOption);
                }
            });
        }

        loadQuestion() {
            this.isAnswered = false;
            const questionData = this.questions[this.currentQuestionIndex];

            // Sadece içerikleri güncelle
            this.elements.question.textContent = questionData.question;

            // Meta tag içeriklerini güncelle
            const metaTags = this.elements.quizInfo.querySelector('.quiz-meta-tags');
            if (metaTags) {
                metaTags.innerHTML = `
                    <span class="quiz-subject">${questionData.subject}</span>
                    <span class="quiz-difficulty">${questionData.difficulty}</span>
                `;
            }

            // Seçenek içeriklerini güncelle (var olanları silip yeniden ekle, container yapısını değiştirme)
            this.elements.optionsContainer.innerHTML = '';
            const optionLetters = ['A', 'B', 'C', 'D'];
            questionData.options.forEach((option, index) => {
                const optionElement = document.createElement('div');
                optionElement.className = 'option';
                optionElement.setAttribute('data-correct', option.correct ? 'true' : 'false');
                optionElement.innerHTML = `
                    <div class="option-letter">${optionLetters[index]}</div>
                    <div class="option-text">${option.text}</div>
                `;
                this.elements.optionsContainer.appendChild(optionElement);
            });

            // Timer'ı başlat
            this.timeLeft = this.timerDuration;
            this.startTimer();

            // Chat'i sıfırla
            this.resetChat();
        }

        handleAnswer(selectedOption) {
            if (this.isAnswered) return;

            this.isAnswered = true;
            this.clearTimer();

            const isCorrect = selectedOption.getAttribute('data-correct') === 'true';
            this.showResult(isCorrect, selectedOption);

            // Doğru cevabı da göster
            const correctOption = this.elements.optionsContainer.querySelector('.option[data-correct="true"]');
            if (correctOption && !isCorrect) {
                correctOption.classList.add('correct');
            }

            // AI mesajını ekle
            const questionData = this.questions[this.currentQuestionIndex];
            const selectedIndex = Array.from(this.elements.optionsContainer.children).indexOf(selectedOption);
            const selectedOptionData = questionData.options[selectedIndex];

            const explanation = isCorrect 
                ? (questionData.correct_explanation || selectedOptionData.explanation || 'Harika! Doğru cevap!')
                : (selectedOptionData.explanation || 'Bu cevap yanlış. Doğru cevabı kontrol edin.');

            this.addAIMessage(explanation, () => {
                setTimeout(() => this.nextQuestion(), 500);
            });
        }

        showResult(isCorrect, selectedOption) {
            selectedOption.classList.add('selected');
            if (isCorrect) {
                selectedOption.classList.add('correct');
            } else {
                selectedOption.classList.add('incorrect');
            }
        }

        nextQuestion() {
            this.currentQuestionIndex = (this.currentQuestionIndex + 1) % this.questions.length;
            this.loadQuestion();
        }

        resetChat() {
            this.elements.chatMessages.innerHTML = '';
            this.addAIMessage('Merhaba! Size bu soru hakkında yardımcı olabilirim. Hangi seçeneği düşünüyorsunuz?');
        }

        addAIMessage(html, cb) {
            this.addMessageAnimated(html, 'ai', cb);
        }

        addUserMessage(text, cb) {
            this.addMessageAnimated(text, 'user', cb);
        }

        addMessageAnimated(content, type, cb) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            
            const time = new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
            
            if (type === 'ai') {
                messageDiv.innerHTML = `
                    <div class="message-content">
                        <p>${content}</p>
                    </div>
                    <div class="message-time">${time}</div>
                `;
            } else {
                messageDiv.innerHTML = `
                    <div class="message-content">
                        <p>${content}</p>
                    </div>
                    <div class="message-time">${time}</div>
                `;
            }

            this.elements.chatMessages.appendChild(messageDiv);
            this.scrollToBottom();

            if (type === 'ai') {
                // Typewriter efekti
                const p = messageDiv.querySelector('p');
                const plainText = p.textContent;
                p.textContent = '';
                let i = 0;

                const typeNext = () => {
                    if (i <= plainText.length) {
                        p.textContent = plainText.slice(0, i);
                        i++;
                        this.scrollToBottom(); // Her karakter eklenirken scroll
                        setTimeout(typeNext, 18);
                    } else if (cb) {
                        cb();
                    }
                };
                typeNext();
            } else if (cb) {
                cb();
            }
        }

        scrollToBottom() {
            this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        }

        startTimer() {
            this.timeLeft = this.timerDuration; // Timer başlangıcında timeLeft'i set et
            this.updateTimerDisplay();
            this.timer = setInterval(() => {
                this.timeLeft--;
                this.updateTimerDisplay();
                
                if (this.timeLeft <= 0) {
                    this.clearTimer();
                    if (!this.isAnswered) {
                        // Süre dolduysa doğru cevabı göster
                        const correctOption = this.elements.optionsContainer.querySelector('.option[data-correct="true"]');
                        
                        if (correctOption) {
                            this.isAnswered = true;
                            correctOption.classList.add('selected', 'correct');
                            
                            const questionData = this.questions[this.currentQuestionIndex];
                            const correctOptionIndex = Array.from(this.elements.optionsContainer.children).indexOf(correctOption);
                            const correctOptionData = questionData.options[correctOptionIndex];
                            
                            this.addAIMessage(questionData.correct_explanation || correctOptionData.explanation || 'Süre doldu! Doğru cevap budur!', () => {
                                setTimeout(() => this.nextQuestion(), 2000); // Biraz daha uzun bekle
                            });
                        }
                    }
                }
            }, 1000);
        }

        updateTimerDisplay() {
            const timerElement = document.getElementById('quiz-timer-value');
            if (timerElement) {
                const minutes = Math.floor(this.timeLeft / 60);
                const seconds = this.timeLeft % 60;
                timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }

        clearTimer() {
            if (this.timer) {
                clearInterval(this.timer);
                this.timer = null;
            }
        }
    }
}