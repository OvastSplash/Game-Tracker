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
    container.style.transform = 'translateY(20px)';
    
    // Задержка для формы, чтобы она появилась после фона
    setTimeout(() => {
        container.style.transition = 'all 0.6s ease';
        container.style.opacity = '1';
        container.style.transform = 'translateY(0)';
    }, 500);

    // Анимация полей при фокусе
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        const input = group.querySelector('input');
        const label = group.querySelector('label');

        if (input && label) {
            // Добавляем эффект при фокусе
            input.addEventListener('focus', () => {
                label.style.transition = 'all 0.3s ease';
                label.style.color = '#7289da';
                label.style.transform = 'translateY(-2px)';
            });

            // Возвращаем в исходное состояние при потере фокуса
            input.addEventListener('blur', () => {
                label.style.color = '';
                label.style.transform = 'translateY(0)';
            });

            // Эффект пульсации при вводе
            input.addEventListener('input', () => {
                group.style.transform = 'translateX(2px)';
                setTimeout(() => {
                    group.style.transform = 'translateX(0)';
                }, 100);
            });
        }
    });

    // Анимация кнопки при наведении
    const submitBtn = document.querySelector('.submit-btn');
    if (submitBtn) {
        submitBtn.addEventListener('mouseover', () => {
            submitBtn.style.transition = 'all 0.3s ease';
            const randomColor = `rgb(${114 + Math.random() * 30}, ${137 + Math.random() * 30}, ${218 + Math.random() * 30})`;
            submitBtn.style.backgroundColor = randomColor;
        });

        submitBtn.addEventListener('mouseout', () => {
            submitBtn.style.backgroundColor = '';
        });

        // Эффект нажатия
        submitBtn.addEventListener('mousedown', () => {
            submitBtn.style.transform = 'scale(0.95)';
        });

        submitBtn.addEventListener('mouseup', () => {
            submitBtn.style.transform = '';
        });
    }

    // Анимация ошибок
    const errorLists = document.querySelectorAll('.errorlist');
    errorLists.forEach(list => {
        list.style.opacity = '0';
        list.style.transform = 'translateX(-10px)';
        
        setTimeout(() => {
            list.style.transition = 'all 0.3s ease';
            list.style.opacity = '1';
            list.style.transform = 'translateX(0)';
        }, 100);
    });

    // Анимация ссылок
    const links = document.querySelectorAll('.additional-links a');
    links.forEach(link => {
        link.addEventListener('mouseover', () => {
            link.style.transition = 'all 0.3s ease';
            link.style.textShadow = '0 0 10px rgba(114, 137, 218, 0.5)';
        });

        link.addEventListener('mouseout', () => {
            link.style.textShadow = '';
        });
    });
}); 