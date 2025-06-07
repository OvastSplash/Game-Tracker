document.addEventListener('DOMContentLoaded', function() {
    // Анимация фонового изображения
    const backgroundImage = document.querySelector('.background-image');
    if (backgroundImage) {
        // Начинаем с полностью темного фона
        backgroundImage.style.opacity = '0';
        
        // Плавно проявляем изображение
        setTimeout(() => {
            backgroundImage.style.opacity = '1';
        }, 100);
    }

    // Анимация появления формы
    const container = document.querySelector('.registration-container');
    container.style.opacity = '0';
    container.style.transform = 'translateY(30px) scale(0.95)';
    
    // Задержка для формы, чтобы она появилась после фона
    setTimeout(() => {
        container.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
        container.style.opacity = '1';
        container.style.transform = 'translateY(0) scale(1)';
    }, 300);

    // Анимация полей при фокусе
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        const input = group.querySelector('input');
        const label = group.querySelector('label');

        if (input && label) {
            // Добавляем эффект при фокусе
            input.addEventListener('focus', () => {
                label.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
                label.style.color = '#00ff88';
                label.style.transform = 'translateY(-3px) scale(1.05)';
                label.style.textShadow = '0 0 10px rgba(0, 255, 136, 0.4)';
            });

            // Возвращаем в исходное состояние при потере фокуса
            input.addEventListener('blur', () => {
                label.style.color = '';
                label.style.transform = 'translateY(0) scale(1)';
                label.style.textShadow = '';
            });

            // Эффект пульсации при вводе
            input.addEventListener('input', () => {
                group.style.transition = 'transform 0.2s ease';
                group.style.transform = 'translateX(3px)';
                setTimeout(() => {
                    group.style.transform = 'translateX(0)';
                }, 150);
            });
        }
    });

    // Анимация кнопки при наведении
    const submitBtn = document.querySelector('.submit-btn');
    if (submitBtn) {
        submitBtn.addEventListener('mouseover', () => {
            submitBtn.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            // Случайные вариации зеленого цвета для динамичности
            const greenVariations = [
                'linear-gradient(45deg, #00ff88, #00cc66)',
                'linear-gradient(45deg, #00cc66, #10b981)', 
                'linear-gradient(45deg, #00ff88, #059669)'
            ];
            const randomGradient = greenVariations[Math.floor(Math.random() * greenVariations.length)];
            submitBtn.style.background = randomGradient;
            submitBtn.style.boxShadow = '0 15px 40px rgba(0, 255, 136, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3)';
        });

        submitBtn.addEventListener('mouseout', () => {
            submitBtn.style.background = '';
            submitBtn.style.boxShadow = '';
        });

        // Эффект нажатия
        submitBtn.addEventListener('mousedown', () => {
            submitBtn.style.transform = 'translateY(-2px) scale(0.98)';
            submitBtn.style.boxShadow = '0 8px 25px rgba(0, 255, 136, 0.4)';
        });

        submitBtn.addEventListener('mouseup', () => {
            submitBtn.style.transform = '';
            submitBtn.style.boxShadow = '';
        });
    }

    // Анимация ошибок
    const errorLists = document.querySelectorAll('.errorlist');
    errorLists.forEach(list => {
        list.style.opacity = '0';
        list.style.transform = 'translateX(-15px) scale(0.95)';
        
        setTimeout(() => {
            list.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            list.style.opacity = '1';
            list.style.transform = 'translateX(0) scale(1)';
        }, 200);
    });

    // Анимация ссылок
    const links = document.querySelectorAll('.additional-links a');
    links.forEach(link => {
        link.addEventListener('mouseover', () => {
            link.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            link.style.textShadow = '0 0 15px rgba(0, 255, 136, 0.6)';
            link.style.transform = 'scale(1.08)';
        });

        link.addEventListener('mouseout', () => {
            link.style.textShadow = '';
            link.style.transform = 'scale(1)';
        });
    });

    // Добавляем интерактивные эффекты для инпутов
    const inputs = document.querySelectorAll('.form-group input');
    inputs.forEach(input => {
        // Эффект волн при клике
        input.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
            ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(0, 255, 136, 0.3)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'ripple 0.6s linear';
            ripple.style.pointerEvents = 'none';
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Добавляем CSS для анимации волн
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .form-group input:focus {
            animation: focusPulse 2s infinite;
        }
        
        @keyframes focusPulse {
            0% { box-shadow: 0 0 20px rgba(0, 255, 136, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1); }
            50% { box-shadow: 0 0 30px rgba(0, 255, 136, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15); }
            100% { box-shadow: 0 0 20px rgba(0, 255, 136, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1); }
        }
    `;
    document.head.appendChild(style);
}); 