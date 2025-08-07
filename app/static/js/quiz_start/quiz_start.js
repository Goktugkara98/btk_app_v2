// =============================================================================
// Quiz Start JavaScript - Multi-Mode Support
// Sınav başlatma ekranı için JavaScript modülü
// =============================================================================

class QuizStartManager {
    constructor() {
        this.currentStep = 1;
        this.formData = {
            quiz_mode: 'normal', // Default to normal mode
            grade_id: '',
            subject_id: '',
            unit_id: '',
            topic_id: '',
            difficulty: 'random',
            timer_enabled: true,
            timer_duration: 30,
            question_count: 20
        };
        
        // Cache for loaded data
        this.grades = [];
        this.subjects = [];
        this.units = [];
        this.topics = [];
        
        this.init();
    }

    async init() {
        console.log('🚀 QuizStartManager başlatılıyor...');
        try {
            await this.loadGrades();
            this.bindEvents();
            this.updatePreview();
            this.validateStep1();
            console.log('✅ QuizStartManager başlatıldı');
        } catch (error) {
            console.error('❌ QuizStartManager başlatılırken hata:', error);
        }
    }

    bindEvents() {
        // Step navigation
        const nextBtn = document.getElementById('next-step-btn');
        const nextBtn2 = document.getElementById('next-step-btn-2');
        const prevBtn = document.getElementById('prev-step-btn');
        const prevBtn2 = document.getElementById('prev-step-btn-2');
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextStep());
        }
        if (nextBtn2) {
            nextBtn2.addEventListener('click', () => this.nextStep());
        }
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prevStep());
        }
        if (prevBtn2) {
            prevBtn2.addEventListener('click', () => this.prevStep());
        }

        // Quiz mode selection
        document.querySelectorAll('input[name="quiz_mode"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.handleQuizModeChange(e));
        });

        // Form controls
        const classSelect = document.getElementById('class-select');
        const subjectSelect = document.getElementById('subject-select');
        const unitSelect = document.getElementById('unit-select');
        const topicSelect = document.getElementById('topic-select');
        
        if (classSelect) {
            classSelect.addEventListener('change', (e) => this.handleClassChange(e));
        }
        if (subjectSelect) {
            subjectSelect.addEventListener('change', (e) => this.handleSubjectChange(e));
        }
        if (unitSelect) {
            unitSelect.addEventListener('change', (e) => this.handleUnitChange(e));
        }
        if (topicSelect) {
            topicSelect.addEventListener('change', (e) => this.handleTopicChange(e));
        }

        // Difficulty selection
        document.querySelectorAll('input[name="difficulty"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.handleDifficultyChange(e));
        });

        // Timer settings
        const timerInput = document.getElementById('timer-minutes');
        if (timerInput) {
            timerInput.addEventListener('change', (e) => this.handleTimerDurationChange(e));
        }

        // Question count
        const questionCountInput = document.getElementById('question-count');
        if (questionCountInput) {
            questionCountInput.addEventListener('change', (e) => this.handleQuestionCountChange(e));
        }

        // Action buttons
        const startBtn = document.getElementById('start-quiz-btn');
        const resetBtn = document.getElementById('reset-settings-btn');
        
        if (startBtn) {
            console.log('🔗 Start quiz butonu bulundu, event listener ekleniyor...');
            startBtn.addEventListener('click', () => {
                console.log('🖱️ Start quiz butonuna tıklandı!');
                this.startQuiz();
            });
        } else {
            console.log('❌ Start quiz butonu bulunamadı!');
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetSettings());
        }
    }

    // Step Navigation
    nextStep() {
        if (this.currentStep === 1) {
            if (this.validateStep1()) {
                this.showStep(2);
            }
        } else if (this.currentStep === 2) {
            if (this.validateStep2()) {
                this.showStep(3);
            }
        }
    }

    prevStep() {
        if (this.currentStep === 2) {
            this.showStep(1);
        } else if (this.currentStep === 3) {
            this.showStep(2);
        }
    }

    showStep(stepNumber) {
        console.log(`🔄 Step ${stepNumber} gösteriliyor...`);
        
        // Hide all steps
        document.querySelectorAll('.form-step').forEach(step => {
            step.classList.remove('active');
        });

        // Show target step
        const targetStep = document.getElementById(`step-${stepNumber}`);
        if (targetStep) {
            targetStep.classList.add('active');
        }

        // Update step indicator
        document.querySelectorAll('.step').forEach((step, index) => {
            step.classList.remove('active', 'completed');
            if (index + 1 < stepNumber) {
                step.classList.add('completed');
            } else if (index + 1 === stepNumber) {
                step.classList.add('active');
            }
        });

        this.currentStep = stepNumber;
        this.updatePreview();
        this.validateCurrentStep();
    }

    // Form Handlers
    handleQuizModeChange(event) {
        const quizMode = event.target.value;
        console.log('🎮 Quiz modu değişti:', quizMode);
        this.formData.quiz_mode = quizMode;
        
        // Educational modda timer'ı devre dışı bırak
        if (quizMode === 'educational') {
            this.formData.timer_enabled = false;
            this.hideElement('timer-group');
        } else {
            this.formData.timer_enabled = true;
            this.showElement('timer-group');
        }
        
        this.updatePreview();
        this.validateStep1();
    }

    handleClassChange(event) {
        const gradeId = event.target.value;
        console.log('🏫 Sınıf değişti:', gradeId);
        this.formData.grade_id = gradeId;
        
        if (gradeId) {
            this.loadSubjects(gradeId);
            this.showElement('subject-group');
        } else {
            this.hideElement('subject-group');
            this.hideElement('unit-group');
            this.hideElement('topic-group');
            this.formData.subject_id = '';
            this.formData.unit_id = '';
            this.formData.topic_id = '';
        }
        
        this.updatePreview();
        this.validateStep2();
    }

    handleSubjectChange(event) {
        const subjectId = event.target.value;
        console.log('📚 Ders değişti:', subjectId);
        this.formData.subject_id = subjectId;
        
        if (subjectId && subjectId !== 'random') {
            this.loadUnits(subjectId);
            this.showElement('unit-group');
        } else {
            this.hideElement('unit-group');
            this.hideElement('topic-group');
            this.formData.unit_id = '';
            this.formData.topic_id = '';
        }
        
        this.updatePreview();
        this.validateStep2();
    }

    handleUnitChange(event) {
        const unitId = event.target.value;
        console.log('📖 Ünite değişti:', unitId);
        this.formData.unit_id = unitId;
        
        if (unitId && unitId !== 'random') {
            this.loadTopics(unitId);
            this.showElement('topic-group');
        } else {
            this.hideElement('topic-group');
            this.formData.topic_id = '';
        }
        
        this.updatePreview();
        this.validateStep2();
    }

    handleTopicChange(event) {
        const topicId = event.target.value;
        console.log('📝 Konu değişti:', topicId);
        this.formData.topic_id = topicId;
        this.updatePreview();
        this.validateStep2();
    }

    handleDifficultyChange(event) {
        this.formData.difficulty = event.target.value;
        this.updatePreview();
    }

    handleTimerDurationChange(event) {
        this.formData.timer_duration = parseInt(event.target.value) || 30;
        this.updatePreview();
    }

    handleQuestionCountChange(event) {
        this.formData.question_count = parseInt(event.target.value) || 20;
        this.updatePreview();
    }

    // Data Loading
    async loadGrades() {
        try {
            console.log('📚 Sınıflar yükleniyor...');
            const response = await fetch('/api/quiz/grades');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('📄 API yanıtı:', data);
            
            if (data.status === 'success') {
                this.grades = data.data;
                this.populateGradesSelect();
                console.log('✅ Sınıflar yüklendi:', this.grades.length);
            } else {
                console.error('❌ Sınıflar yüklenirken hata:', data.message);
                this.showError('Sınıflar yüklenirken hata oluştu: ' + data.message);
            }
        } catch (error) {
            console.error('❌ Sınıflar yüklenirken hata:', error);
            this.showError('Sınıflar yüklenirken hata oluştu: ' + error.message);
        }
    }

    async loadSubjects(gradeId) {
        try {
            console.log('📖 Dersler yükleniyor... (grade_id:', gradeId, ')');
            const response = await fetch(`/api/quiz/subjects?grade_id=${gradeId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.subjects = data.data;
                this.populateSubjectsSelect();
                console.log('✅ Dersler yüklendi:', this.subjects.length);
            } else {
                console.error('❌ Dersler yüklenirken hata:', data.message);
            }
        } catch (error) {
            console.error('❌ Dersler yüklenirken hata:', error);
        }
    }

    async loadUnits(subjectId) {
        try {
            console.log('📚 Üniteler yükleniyor... (subject_id:', subjectId, ')');
            const response = await fetch(`/api/quiz/units?subject_id=${subjectId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.units = data.data;
                this.populateUnitsSelect();
                console.log('✅ Üniteler yüklendi:', this.units.length);
            } else {
                console.error('❌ Üniteler yüklenirken hata:', data.message);
            }
        } catch (error) {
            console.error('❌ Üniteler yüklenirken hata:', error);
        }
    }

    async loadTopics(unitId) {
        try {
            console.log('📝 Konular yükleniyor... (unit_id:', unitId, ')');
            const response = await fetch(`/api/quiz/topics?unit_id=${unitId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.topics = data.data;
                this.populateTopicsSelect();
                console.log('✅ Konular yüklendi:', this.topics.length);
            } else {
                console.error('❌ Konular yüklenirken hata:', data.message);
            }
        } catch (error) {
            console.error('❌ Konular yüklenirken hata:', error);
        }
    }

    populateGradesSelect() {
        const select = document.getElementById('class-select');
        if (!select) return;

        // Clear existing options except the first one
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }

        // Add new options
        this.grades.forEach(grade => {
            const option = document.createElement('option');
            option.value = grade.id;
            option.textContent = grade.name;
            select.appendChild(option);
        });
    }

    populateSubjectsSelect() {
        const select = document.getElementById('subject-select');
        if (!select) return;

        // Clear all existing options
        select.innerHTML = '';

        // Add "Random" option
        const randomOption = document.createElement('option');
        randomOption.value = 'random';
        randomOption.textContent = 'Rasgele Ders';
        select.appendChild(randomOption);

        // Add new options
        this.subjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject.id;
            option.textContent = subject.name;
            select.appendChild(option);
        });

        // Enable the select
        select.disabled = false;
    }

    populateUnitsSelect() {
        const select = document.getElementById('unit-select');
        if (!select) return;

        // Clear all existing options
        select.innerHTML = '';

        // Add "Random" option
        const randomOption = document.createElement('option');
        randomOption.value = 'random';
        randomOption.textContent = 'Rasgele Ünite';
        select.appendChild(randomOption);

        // Add new options
        this.units.forEach(unit => {
            const option = document.createElement('option');
            option.value = unit.id;
            option.textContent = unit.name;
            select.appendChild(option);
        });

        // Enable the select
        select.disabled = false;
    }

    populateTopicsSelect() {
        const select = document.getElementById('topic-select');
        if (!select) return;

        // Clear all existing options
        select.innerHTML = '';

        // Add "Random" option
        const randomOption = document.createElement('option');
        randomOption.value = 'random';
        randomOption.textContent = 'Rasgele Konu';
        select.appendChild(randomOption);

        // Add new options
        this.topics.forEach(topic => {
            const option = document.createElement('option');
            option.value = topic.id;
            option.textContent = topic.name;
            select.appendChild(option);
        });

        // Enable the select
        select.disabled = false;
    }

    // Validation
    validateStep1() {
        // Step 1 only requires quiz mode selection
        const isValid = this.formData.quiz_mode;
        
        console.log('🔍 Step 1 validation:', {
            quiz_mode: this.formData.quiz_mode,
            isValid: isValid
        });
        
        const nextBtn = document.getElementById('next-step-btn');
        if (nextBtn) {
            nextBtn.disabled = !isValid;
        }
        
        return isValid;
    }

    validateStep2() {
        // Step 2 requires grade_id and subject_id
        const isValid = this.formData.grade_id && this.formData.subject_id;
        
        console.log('🔍 Step 2 validation:', {
            grade_id: this.formData.grade_id,
            subject_id: this.formData.subject_id,
            isValid: isValid
        });
        
        const nextBtn = document.getElementById('next-step-btn-2');
        if (nextBtn) {
            nextBtn.disabled = !isValid;
        }
        
        return isValid;
    }

    validateCurrentStep() {
        if (this.currentStep === 1) {
            return this.validateStep1();
        } else if (this.currentStep === 2) {
            return this.validateStep2();
        }
        return true;
    }

    // Preview Updates
    updatePreview() {
        this.updatePreviewItem('mode', this.getQuizModeName(this.formData.quiz_mode));
        this.updatePreviewItem('class', this.getGradeName(this.formData.grade_id));
        this.updatePreviewItem('subject', this.getSubjectName(this.formData.subject_id));
        this.updatePreviewItem('unit', this.getUnitName(this.formData.unit_id));
        this.updatePreviewItem('topic', this.getTopicName(this.formData.topic_id));
        this.updatePreviewItem('difficulty', this.getDifficultyName(this.formData.difficulty));
        this.updatePreviewItem('timer', this.getTimerText());
        this.updatePreviewItem('question-count', this.getQuestionCountText());
        
        this.validateForm();
    }

    updatePreviewItem(field, value) {
        const element = document.getElementById(`preview-${field}`);
        if (element) {
            element.textContent = value || '-';
        }
    }

    getQuizModeName(quizMode) {
        const modeMap = {
            'normal': 'Normal Quiz',
            'educational': 'Öğretici Quiz'
        };
        return modeMap[quizMode] || 'Normal Quiz';
    }

    getGradeName(gradeId) {
        if (!gradeId) return '-';
        const grade = this.grades.find(g => g.id == gradeId);
        return grade ? grade.name : '-';
    }

    getSubjectName(subjectId) {
        if (!subjectId) return '-';
        if (subjectId === 'random') return 'Rasgele Ders';
        const subject = this.subjects.find(s => s.id == subjectId);
        return subject ? subject.name : '-';
    }

    getUnitName(unitId) {
        if (!unitId) return '-';
        if (unitId === 'random') return 'Rasgele Ünite';
        const unit = this.units.find(u => u.id == unitId);
        return unit ? unit.name : '-';
    }

    getTopicName(topicId) {
        if (!topicId) return '-';
        if (topicId === 'random') return 'Rasgele Konu';
        const topic = this.topics.find(t => t.id == topicId);
        return topic ? topic.name : '-';
    }

    getDifficultyName(difficulty) {
        const difficultyMap = {
            'random': 'Karışık',
            'easy': 'Kolay',
            'medium': 'Orta',
            'hard': 'Zor'
        };
        return difficultyMap[difficulty] || 'Karışık';
    }

    getTimerText() {
        if (this.formData.quiz_mode === 'educational') {
            return 'Süresiz';
        }
        return `${this.formData.timer_duration} dakika`;
    }

    getQuestionCountText() {
        return `${this.formData.question_count} soru`;
    }

    validateForm() {
        // For final validation, require quiz mode, grade_id and subject_id
        const isValid = this.formData.quiz_mode && this.formData.grade_id && this.formData.subject_id;
        
        console.log('🔍 Final validation:', {
            quiz_mode: this.formData.quiz_mode,
            grade_id: this.formData.grade_id,
            subject_id: this.formData.subject_id,
            isValid: isValid
        });
        
        const startBtn = document.getElementById('start-quiz-btn');
        if (startBtn) {
            startBtn.disabled = !isValid;
        }
        
        this.showValidation(isValid);
        
        return isValid;
    }

    showValidation(isValid) {
        const container = document.getElementById('validation-container');
        if (!container) return;

        container.innerHTML = '';
        
        if (!isValid) {
            container.innerHTML = `
                <div class="validation-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    Sınav başlatmak için quiz modu, sınıf ve ders seçimi yapın
                </div>
            `;
        }
    }

    // UI Helpers
    showElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'block';
        }
    }

    hideElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
        }
    }

    // Quiz Actions
    async startQuiz() {
        console.log('🚀 startQuiz() çağrıldı');
        console.log('📋 Form verileri:', this.formData);
        
        if (!this.validateForm()) {
            console.log('❌ Form validasyonu başarısız');
            return;
        }
        
        console.log('✅ Form validasyonu başarılı');

        const startBtn = document.getElementById('start-quiz-btn');
        if (startBtn) {
            startBtn.disabled = true;
            startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sınav Başlatılıyor...';
        }

        try {
            console.log('🌐 API çağrısı yapılıyor...');
            const response = await fetch('/api/quiz/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.formData)
            });

            console.log('📡 API yanıtı:', response.status);
            const data = await response.json();
            console.log('📄 API verisi:', data);

            if (data.status === 'success') {
                console.log('✅ Quiz oturumu oluşturuldu, yönlendiriliyor...');
                // Quiz moduna göre doğru sayfaya yönlendir
                const quizUrl = this.formData.quiz_mode === 'educational' 
                    ? `/quiz/educational?session_id=${data.data.session_id}`
                    : `/quiz/normal?session_id=${data.data.session_id}`;
                window.location.href = quizUrl;
            } else {
                console.log('❌ API hatası:', data.message);
                this.showError(data.message || 'Sınav başlatılırken bir hata oluştu');
            }
        } catch (error) {
            console.error('❌ Quiz başlatılırken hata:', error);
            this.showError('Sınav başlatılırken bir hata oluştu: ' + error.message);
        } finally {
            if (startBtn) {
                startBtn.disabled = false;
                startBtn.innerHTML = '<i class="fas fa-play"></i> Sınavı Başlat';
            }
        }
    }

    resetSettings() {
        // Form verilerini sıfırla
        this.formData = {
            quiz_mode: 'normal',
            grade_id: '',
            subject_id: '',
            unit_id: '',
            topic_id: '',
            difficulty: 'random',
            timer_enabled: true,
            timer_duration: 30,
            question_count: 20
        };

        // Form elemanlarını sıfırla
        const normalModeRadio = document.querySelector('input[name="quiz_mode"][value="normal"]');
        if (normalModeRadio) normalModeRadio.checked = true;

        const classSelect = document.getElementById('class-select');
        const subjectSelect = document.getElementById('subject-select');
        const unitSelect = document.getElementById('unit-select');
        const topicSelect = document.getElementById('topic-select');
        
        if (classSelect) classSelect.value = '';
        if (subjectSelect) {
            subjectSelect.value = '';
            subjectSelect.disabled = true;
            subjectSelect.innerHTML = '<option value="">Ders seçiniz</option>';
        }
        if (unitSelect) {
            unitSelect.value = '';
            unitSelect.disabled = true;
            unitSelect.innerHTML = '<option value="">Ünite seçiniz</option>';
        }
        if (topicSelect) {
            topicSelect.value = '';
            topicSelect.disabled = true;
            topicSelect.innerHTML = '<option value="">Konu seçiniz</option>';
        }

        // Radio button'ları sıfırla
        const randomDifficulty = document.querySelector('input[name="difficulty"][value="random"]');
        if (randomDifficulty) randomDifficulty.checked = true;

        // Input değerlerini sıfırla
        const timerInput = document.getElementById('timer-minutes');
        const questionCountInput = document.getElementById('question-count');
        
        if (timerInput) timerInput.value = 30;
        if (questionCountInput) questionCountInput.value = 20;

        // UI'yi güncelle
        this.showElement('timer-group');
        this.hideElement('subject-group');
        this.hideElement('unit-group');
        this.hideElement('topic-group');
        this.showStep(1);
        this.updatePreview();
        this.validateStep1();
    }

    showError(message) {
        const container = document.getElementById('validation-container');
        if (container) {
            container.innerHTML = `
                <div class="validation-error">
                    <i class="fas fa-times-circle"></i>
                    ${message}
                </div>
            `;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM yüklendi, QuizStartManager oluşturuluyor...');
    new QuizStartManager();
    console.log('✅ QuizStartManager oluşturuldu');
}); 