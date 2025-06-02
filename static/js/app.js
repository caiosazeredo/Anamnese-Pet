// Configurações globais
const APP_CONFIG = {
    baseUrl: window.location.origin,
    ajaxTimeout: 30000,
    autoSaveInterval: 10000
};

// Utilitários gerais
const Utils = {
    
    // Formatação de CPF
    formatCPF(cpf) {
        return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    },
    
    // Formatação de telefone
    formatPhone(phone) {
        return phone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    },
    
    // Validação de CPF
    validateCPF(cpf) {
        cpf = cpf.replace(/[^\d]/g, '');
        
        if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) {
            return false;
        }
        
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cpf.charAt(i)) * (10 - i);
        }
        
        let remainder = 11 - (sum % 11);
        if (remainder === 10 || remainder === 11) remainder = 0;
        if (remainder !== parseInt(cpf.charAt(9))) return false;
        
        sum = 0;
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cpf.charAt(i)) * (11 - i);
        }
        
        remainder = 11 - (sum % 11);
        if (remainder === 10 || remainder === 11) remainder = 0;
        
        return remainder === parseInt(cpf.charAt(10));
    },
    
    // Mostrar loading
    showLoading(element) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (element) {
            element.disabled = true;
            const originalText = element.textContent;
            element.dataset.originalText = originalText;
            element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Carregando...';
        }
    },
    
    // Ocultar loading
    hideLoading(element) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (element) {
            element.disabled = false;
            const originalText = element.dataset.originalText;
            if (originalText) {
                element.textContent = originalText;
            }
        }
    },
    
    // Mostrar notificação toast
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 5000
        });
        
        bsToast.show();
        
        // Remover elemento após ocultar
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },
    
    // Criar container de toasts
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    },
    
    // Confirmar ação
    confirm(message, callback) {
        if (window.confirm(message)) {
            callback();
        }
    },
    
    // Debounce para otimizar eventos
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Gerenciador de AJAX
const AjaxManager = {
    
    // Request padrão
    request(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            timeout: APP_CONFIG.ajaxTimeout
        };
        
        const config = { ...defaultOptions, ...options };
        
        // Adicionar CSRF token se disponível
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken.getAttribute('content');
        }
        
        return fetch(url, config)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('Ajax Error:', error);
                Utils.showToast('Erro de conexão. Tente novamente.', 'danger');
                throw error;
            });
    },
    
    // GET request
    get(url, params = {}) {
        const urlWithParams = new URL(url, APP_CONFIG.baseUrl);
        Object.keys(params).forEach(key => {
            urlWithParams.searchParams.append(key, params[key]);
        });
        
        return this.request(urlWithParams.toString());
    },
    
    // POST request
    post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    // PUT request
    put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    // DELETE request
    delete(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }
};

// Gerenciador de formulários
const FormManager = {
    
    // Configurar formulário
    setup(formId, options = {}) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        const config = {
            validateOnSubmit: true,
            showValidationFeedback: true,
            autoSave: false,
            ...options
        };
        
        // Configurar validação
        if (config.validateOnSubmit) {
            form.addEventListener('submit', (e) => {
                if (!this.validate(form)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        }
        
        // Configurar auto-save
        if (config.autoSave) {
            TabletUtils.enableAutoSave(formId);
        }
        
        // Configurar máscaras
        this.setupMasks(form);
        
        return form;
    },
    
    // Configurar máscaras
    setupMasks(form) {
        // CPF
        form.querySelectorAll('input[name*="cpf"]').forEach(input => {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                value = value.replace(/(\d{3})(\d)/, '$1.$2');
                value = value.replace(/(\d{3})(\d)/, '$1.$2');
                value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
                e.target.value = value;
            });
        });
        
        // Telefone
        form.querySelectorAll('input[type="tel"]').forEach(input => {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                value = value.replace(/(\d{2})(\d)/, '($1) $2');
                value = value.replace(/(\d{5})(\d)/, '$1-$2');
                e.target.value = value;
            });
        });
    },
    
    // Validar formulário
    validate(form) {
        let isValid = true;
        
        // Validar campos obrigatórios
        form.querySelectorAll('[required]').forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                this.showFieldError(field, 'Este campo é obrigatório');
            }
        });
        
        // Validar CPF
        form.querySelectorAll('input[name*="cpf"]').forEach(field => {
            if (field.value && !Utils.validateCPF(field.value)) {
                isValid = false;
                this.showFieldError(field, 'CPF inválido');
            }
        });
        
        // Validar email
        form.querySelectorAll('input[type="email"]').forEach(field => {
            if (field.value && !this.validateEmail(field.value)) {
                isValid = false;
                this.showFieldError(field, 'E-mail inválido');
            }
        });
        
        return isValid;
    },
    
    // Validar email
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Mostrar erro em campo
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        let feedback = field.parentNode.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.appendChild(feedback);
        }
        
        feedback.textContent = message;
    },
    
    // Limpar erros
    clearErrors(form) {
        form.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        
        form.querySelectorAll('.invalid-feedback').forEach(feedback => {
            feedback.remove();
        });
    },
    
    // Serializar formulário
    serialize(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        
        return data;
    }
};

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    
    // Configurar tooltips globalmente
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Configurar formulários principais
    const mainForms = ['tutorForm', 'petForm', 'anamneseForm', 'checkinForm', 'checkoutForm'];
    mainForms.forEach(formId => {
        FormManager.setup(formId, {
            validateOnSubmit: true,
            autoSave: true
        });
    });
    
    // Configurar busca com debounce
    document.querySelectorAll('input[data-search]').forEach(input => {
        const debouncedSearch = Utils.debounce((value) => {
            const searchUrl = input.dataset.search;
            if (value.length >= 3) {
                AjaxManager.get(searchUrl, { q: value })
                    .then(results => {
                        // Processar resultados da busca
                        console.log('Resultados:', results);
                    });
            }
        }, 500);
        
        input.addEventListener('input', (e) => {
            debouncedSearch(e.target.value);
        });
    });
    
    // Configurar auto-refresh para páginas de consulta
    if (window.location.pathname.includes('/consultar')) {
        setInterval(() => {
            const lastUpdate = document.querySelector('[data-last-update]');
            if (lastUpdate) {
                const updateTime = new Date(lastUpdate.dataset.lastUpdate);
                const now = new Date();
                
                // Atualizar se passou mais de 1 minuto
                if (now - updateTime > 60000) {
                    location.reload();
                }
            }
        }, 30000);
    }
    
    // Configurar confirmações de exclusão
    document.querySelectorAll('[data-confirm-delete]').forEach(element => {
        element.addEventListener('click', (e) => {
            e.preventDefault();
            
            const message = element.dataset.confirmDelete || 'Tem certeza que deseja excluir este item?';
            
            Utils.confirm(message, () => {
                if (element.href) {
                    window.location.href = element.href;
                } else if (element.dataset.action) {
                    // Executar ação AJAX
                    AjaxManager.delete(element.dataset.action)
                        .then(() => {
                            Utils.showToast('Item excluído com sucesso!', 'success');
                            setTimeout(() => location.reload(), 1000);
                        });
                }
            });
        });
    });
    
    console.log('Sistema PetAnamnese inicializado com sucesso!');
});

// Expor utilitários globalmente para uso em templates
window.PetAnamnese = {
    Utils,
    AjaxManager,
    FormManager,
    TabletUtils
}; 
