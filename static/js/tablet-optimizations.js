/**
 * Otimizações específicas para tablets
 */

// Detectar se é dispositivo touch
const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

// Configurações globais para tablets
if (isTouchDevice) {
    document.body.classList.add('touch-device');
    
    // Aumentar área de toque para botões pequenos
    const style = document.createElement('style');
    style.textContent = `
        .btn-sm {
            min-height: 44px !important;
            min-width: 44px !important;
        }
        
        .form-control, .form-select {
            min-height: 48px !important;
            font-size: 16px !important;
        }
        
        .list-group-item {
            min-height: 60px;
            display: flex;
            align-items: center;
        }
        
        /* Prevenir zoom em inputs no iOS */
        input, select, textarea {
            font-size: 16px !important;
        }
    `;
    document.head.appendChild(style);
}

// Funções utilitárias para tablets
const TabletUtils = {
    
    // Vibração de feedback (se disponível)
    vibrate(pattern = [50]) {
        if (navigator.vibrate) {
            navigator.vibrate(pattern);
        }
    },
    
    // Feedback visual para toque
    addTouchFeedback(element) {
        element.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
            this.style.transition = 'transform 0.1s ease';
        });
        
        element.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    },
    
    // Configurar signature pad para tablets
    setupSignaturePad(canvas, options = {}) {
        const defaultOptions = {
            backgroundColor: 'rgb(255, 255, 255)',
            penColor: 'rgb(0, 0, 0)',
            minWidth: 2,
            maxWidth: 4,
            throttle: 16,
            minDistance: 5
        };
        
        const signaturePad = new SignaturePad(canvas, {...defaultOptions, ...options});
        
        // Redimensionar para alta resolução
        function resizeCanvas() {
            const ratio = Math.max(window.devicePixelRatio || 1, 1);
            canvas.width = canvas.offsetWidth * ratio;
            canvas.height = canvas.offsetHeight * ratio;
            const ctx = canvas.getContext('2d');
            ctx.scale(ratio, ratio);
            signaturePad.clear();
        }
        
        window.addEventListener('orientationchange', () => {
            setTimeout(resizeCanvas, 100);
        });
        
        resizeCanvas();
        
        return signaturePad;
    },
    
    // Modal full screen para tablets
    makeModalFullscreen(modalId) {
        const modal = document.getElementById(modalId);
        if (modal && window.innerWidth <= 768) {
            modal.classList.add('modal-fullscreen');
        }
    },
    
    // Auto-save de formulários
    enableAutoSave(formId, keyPrefix = 'form_') {
        const form = document.getElementById(formId);
        if (!form) return;
        
        const inputs = form.querySelectorAll('input, select, textarea');
        
        // Carregar dados salvos
        inputs.forEach(input => {
            const savedValue = sessionStorage.getItem(keyPrefix + input.name);
            if (savedValue && input.type !== 'password') {
                if (input.type === 'checkbox') {
                    input.checked = savedValue === 'true';
                } else {
                    input.value = savedValue;
                }
            }
        });
        
        // Salvar mudanças automaticamente
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                const value = input.type === 'checkbox' ? input.checked : input.value;
                sessionStorage.setItem(keyPrefix + input.name, value);
            });
        });
        
        // Limpar ao submeter
        form.addEventListener('submit', () => {
            inputs.forEach(input => {
                sessionStorage.removeItem(keyPrefix + input.name);
            });
        });
    },
    
    // Confirmação de saída com dados não salvos
    enableUnsavedWarning(formId) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        let hasUnsavedChanges = false;
        
        form.addEventListener('change', () => {
            hasUnsavedChanges = true;
        });
        
        form.addEventListener('submit', () => {
            hasUnsavedChanges = false;
        });
        
        window.addEventListener('beforeunload', (e) => {
            if (hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = 'Você tem alterações não salvas. Deseja realmente sair?';
                return e.returnValue;
            }
        });
    }
};

// Aplicar otimizações quando documento carregar
document.addEventListener('DOMContentLoaded', function() {
    
    // Adicionar feedback de toque em botões
    document.querySelectorAll('.btn, .card.menu-card, .list-group-item-action').forEach(element => {
        TabletUtils.addTouchFeedback(element);
    });
    
    // Configurar modais fullscreen em tablets
    document.querySelectorAll('.modal').forEach(modal => {
        TabletUtils.makeModalFullscreen(modal.id);
    });
    
    // Auto-save para formulários longos
    const longForms = ['tutorForm', 'petForm', 'anamneseForm'];
    longForms.forEach(formId => {
        TabletUtils.enableAutoSave(formId);
        TabletUtils.enableUnsavedWarning(formId);
    });
    
    // Configurar signature pads
    document.querySelectorAll('.signature-pad').forEach(canvas => {
        if (!canvas.dataset.configured) {
            TabletUtils.setupSignaturePad(canvas);
            canvas.dataset.configured = 'true';
        }
    });
    
    // Melhorar navegação por swipe (opcional)
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    document.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });
    
    function handleSwipe() {
        const swipeThreshold = 100;
        const difference = touchStartX - touchEndX;
        
        if (Math.abs(difference) > swipeThreshold) {
            if (difference > 0) {
                // Swipe left - próxima página
                const nextBtn = document.querySelector('.btn:contains("Próximo"), .btn:contains("Confirmar")');
                if (nextBtn && !nextBtn.disabled) {
                    TabletUtils.vibrate([25]);
                }
            } else {
                // Swipe right - página anterior
                const backBtn = document.querySelector('.btn:contains("Voltar"), .btn:contains("Cancelar")');
                if (backBtn) {
                    TabletUtils.vibrate([25]);
                }
            }
        }
    }
    
    // Feedback visual para ações importantes
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-success') || 
            e.target.classList.contains('btn-primary')) {
            TabletUtils.vibrate([50]);
        }
    });
    
    // Configurar orientação landscape para signature pads
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            // Reconfigurar signature pads após mudança de orientação
            document.querySelectorAll('.signature-pad').forEach(canvas => {
                if (canvas.signaturePad) {
                    canvas.signaturePad.clear();
                }
            });
        }, 500);
    });
});
