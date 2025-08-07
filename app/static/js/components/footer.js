/**
 * FOOTER JAVASCRIPT
 * 
 * Modern footer için etkileşimli özellikler ve newsletter form işlevselliği.
 * =============================================================================
 */

export function initFooter() {
    // Newsletter form işlevselliği
    const newsletterForm = document.getElementById('newsletter-form');
    const newsletterSuccess = document.getElementById('newsletter-success');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', handleNewsletterSubmit);
    }
    
    // Sosyal medya linklerine hover efekti
    initSocialIcons();
    
    // Footer linklerine smooth scroll
    initFooterLinks();
    
    // Footer stats animasyonu
    initFooterStats();
}

/**
 * Newsletter form submit işleyicisi
 */
function handleNewsletterSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const input = form.querySelector('input[type="email"]');
    const email = input.value.trim();
    
    if (!email) {
        showInputError(input, 'E-posta adresi gerekli');
        return;
    }
    
    if (!isValidEmail(email)) {
        showInputError(input, 'Geçerli bir e-posta adresi girin');
        return;
    }
    
    // Form gönderimi simülasyonu
    showLoadingState(form);
    
    // API çağrısı simülasyonu (gerçek uygulamada backend'e gönderilir)
    setTimeout(() => {
        hideLoadingState(form);
        showSuccessMessage();
        form.reset();
        
        // 3 saniye sonra success mesajını gizle
        setTimeout(() => {
            hideSuccessMessage();
        }, 3000);
    }, 1500);
}

/**
 * E-posta formatı doğrulama
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Input hata mesajı göster
 */
function showInputError(input, message) {
    // Mevcut hata mesajını temizle
    const existingError = input.parentNode.querySelector('.input-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Yeni hata mesajı oluştur
    const errorDiv = document.createElement('div');
    errorDiv.className = 'input-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        color: #ef4444;
        font-size: 0.85rem;
        margin-top: 8px;
        font-family: var(--font-family-main);
    `;
    
    input.parentNode.appendChild(errorDiv);
    input.style.borderColor = '#ef4444';
    
    // 3 saniye sonra hata mesajını temizle
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
        input.style.borderColor = 'rgba(255, 255, 255, 0.2)';
    }, 3000);
}

/**
 * Loading durumu göster
 */
function showLoadingState(form) {
    const button = form.querySelector('.newsletter-btn');
    const icon = button.querySelector('i');
    
    button.disabled = true;
    icon.className = 'bi bi-arrow-clockwise';
    icon.style.animation = 'spin 1s linear infinite';
    
    // Spin animasyonu için CSS ekle
    if (!document.querySelector('#spin-animation')) {
        const style = document.createElement('style');
        style.id = 'spin-animation';
        style.textContent = `
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Loading durumunu gizle
 */
function hideLoadingState(form) {
    const button = form.querySelector('.newsletter-btn');
    const icon = button.querySelector('i');
    
    button.disabled = false;
    icon.className = 'bi bi-arrow-right';
    icon.style.animation = '';
}

/**
 * Başarı mesajını göster
 */
function showSuccessMessage() {
    const successElement = document.getElementById('newsletter-success');
    if (successElement) {
        successElement.style.display = 'flex';
        successElement.style.animation = 'fadeInUp 0.5s ease';
        
        // FadeInUp animasyonu için CSS ekle
        if (!document.querySelector('#fade-animation')) {
            const style = document.createElement('style');
            style.id = 'fade-animation';
            style.textContent = `
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

/**
 * Başarı mesajını gizle
 */
function hideSuccessMessage() {
    const successElement = document.getElementById('newsletter-success');
    if (successElement) {
        successElement.style.display = 'none';
    }
}

/**
 * Sosyal medya ikonları için hover efektleri
 */
function initSocialIcons() {
    const socialIcons = document.querySelectorAll('.social-icon');
    
    socialIcons.forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.05)';
        });
        
        icon.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

/**
 * Footer linkleri için smooth scroll
 */
function initFooterLinks() {
    const footerLinks = document.querySelectorAll('.footer-links-group a[href^="#"]');
    
    footerLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Footer stats animasyonu
 */
function initFooterStats() {
    const stats = document.querySelectorAll('.stat-item');
    
    // Intersection Observer ile stats görünür olduğunda animasyon başlat
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInLeft 0.6s ease forwards';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    stats.forEach((stat, index) => {
        stat.style.opacity = '0';
        stat.style.transform = 'translateX(-20px)';
        stat.style.animationDelay = `${index * 0.1}s`;
        observer.observe(stat);
    });
    
    // FadeInLeft animasyonu için CSS ekle
    if (!document.querySelector('#fadeLeft-animation')) {
        const style = document.createElement('style');
        style.id = 'fadeLeft-animation';
        style.textContent = `
            @keyframes fadeInLeft {
                from {
                    opacity: 0;
                    transform: translateX(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Footer'ın görünürlüğünü kontrol et ve gerekirse animasyonları tetikle
 */
export function checkFooterVisibility() {
    const footer = document.querySelector('.footer');
    if (!footer) return;
    
    const rect = footer.getBoundingClientRect();
    const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
    
    if (isVisible) {
        // Footer görünür olduğunda ek animasyonlar tetiklenebilir
        const newsletterCard = document.querySelector('.newsletter-card');
        if (newsletterCard && !newsletterCard.classList.contains('animated')) {
            newsletterCard.classList.add('animated');
            newsletterCard.style.animation = 'slideInUp 0.8s ease';
        }
    }
}

// Sayfa yüklendiğinde footer'ı başlat
document.addEventListener('DOMContentLoaded', () => {
    initFooter();
    
    // Scroll event listener ekle
    window.addEventListener('scroll', checkFooterVisibility);
    
    // Sayfa yüklendiğinde bir kez kontrol et
    setTimeout(checkFooterVisibility, 100);
}); 