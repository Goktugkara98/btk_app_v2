// NAVBAR COMPONENT
import { initNavbar } from './components/navbar.js';
// FOOTER COMPONENT
import { initFooter } from './components/footer.js';
// VIEWPORT UTILITIES
import { initViewportUtils } from './utils/viewport.js';

// Initialize navbar and footer
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initFooter();
    initViewportUtils();
});

// HERO DEMO TIMER (10 saniyelik interaktif demo)
(function() {
    const timerEl = document.getElementById('demo-timer');
    const questionEl = document.getElementById('demo-question');
    const optionsEl = document.getElementById('demo-options');
    const infoEl = document.querySelector('.quiz-info');
    if (!timerEl || !questionEl || !optionsEl || !infoEl) return;

    let timer = 10;
    let interval = null;
    const demoQuestions = [
        {
            q: 'Aşağıdaki sayılardan hangisi en büyüktür?',
            info: { subject: 'Matematik', difficulty: 'Orta' },
            opts: [
                { l: 'A', t: '1250', correct: true },
                { l: 'B', t: '999', correct: false },
                { l: 'C', t: '850', correct: false },
                { l: 'D', t: '750', correct: false }
            ]
        },
        {
            q: 'Türkiye’nin başkenti neresidir?',
            info: { subject: 'Genel Kültür', difficulty: 'Kolay' },
            opts: [
                { l: 'A', t: 'İstanbul', correct: false },
                { l: 'B', t: 'Ankara', correct: true },
                { l: 'C', t: 'İzmir', correct: false },
                { l: 'D', t: 'Bursa', correct: false }
            ]
        },
        {
            q: '5 + 7 işleminin sonucu kaçtır?',
            info: { subject: 'Matematik', difficulty: 'Kolay' },
            opts: [
                { l: 'A', t: '10', correct: false },
                { l: 'B', t: '12', correct: true },
                { l: 'C', t: '13', correct: false },
                { l: 'D', t: '15', correct: false }
            ]
        }
    ];
    let current = 0;

    function renderQuestion(idx) {
        const q = demoQuestions[idx % demoQuestions.length];
        questionEl.textContent = q.q;
        infoEl.innerHTML = `<span class='quiz-subject'>${q.info.subject}</span> <span class='quiz-difficulty'>${q.info.difficulty}</span>`;
        optionsEl.innerHTML = '';
        q.opts.forEach(opt => {
            const div = document.createElement('div');
            div.className = 'option';
            div.setAttribute('data-correct', opt.correct);
            div.innerHTML = `<span class=\"option-letter\">${opt.l}</span><span class=\"option-text\">${opt.t}</span>`;
            div.addEventListener('click', () => {
                clearInterval(interval);
                timer = 10;
                current++;
                renderQuestion(current);
                startTimer();
            });
            optionsEl.appendChild(div);
        });
    }

    function startTimer() {
        timerEl.textContent = timer;
        interval = setInterval(() => {
            timer--;
            timerEl.textContent = timer;
            if (timer <= 0) {
                clearInterval(interval);
                timer = 10;
                current++;
                renderQuestion(current);
                startTimer();
            }
        }, 1000);
    }

    renderQuestion(current);
    startTimer();
})();
