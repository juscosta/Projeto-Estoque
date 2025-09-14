// ========== CONFIGURAÇÕES GLOBAIS ==========
$(document).ready(function() {
    // Inicializar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers do Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts após 5 segundos
    setTimeout(function() {
        $('.alert:not(.alert-permanent)').fadeOut('slow');
    }, 5000);
    
    // Adicionar classe de animação aos cards
    $('.card').addClass('fade-in');
    
    // Configurar validação em tempo real para formulários
    setupFormValidation();
    
    // Configurar ações de confirmação
    setupConfirmActions();
    
    // Configurar navegação por teclado
    setupKeyboardNavigation();
});

// ========== SISTEMA DE ALERTAS ==========
function carregarAlertas() {
    // Verificar se o usuário é admin
    if (!$('#alertasModal').length) {
        showNotification('Acesso negado', 'Apenas administradores podem ver alertas detalhados.', 'warning');
        return;
    }
    
    $('#alertasModal').modal('show');
    
    // Fazer requisição para API de alertas
    $.ajax({
        url: '/api/alertas',
        method: 'GET',
        success: function(data) {
            renderizarAlertas(data);
        },
        error: function() {
            $('#alertas-content').html(`
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    Erro ao carregar alertas. Tente novamente.
                </div>
            `);
        }
    });
}

function renderizarAlertas(data) {
    var content = '';
    
    if (data.total === 0) {
        content = `
            <div class="text-center py-4">
                <i class="bi bi-check-circle display-4 text-success"></i>
                <h5 class="text-success mt-3">Tudo certo!</h5>
                <p class="text-muted">Todos os produtos estão com estoque adequado.</p>
            </div>
        `;
    } else {
        content = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>${data.total}</strong> produto${data.total > 1 ? 's' : ''} com estoque baixo encontrado${data.total > 1 ? 's' : ''}.
            </div>
            <div class="list-group list-group-flush">
        `;
        
        data.produtos.forEach(function(produto) {
            var statusClass = produto.quantidade === 0 ? 'danger' : 'warning';
            var statusText = produto.quantidade === 0 ? 'ZERADO' : 'BAIXO';
            
            content += `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${produto.nome}</h6>
                        <p class="mb-1 text-muted small">Código: ${produto.codigo}</p>
                        <small class="text-${statusClass}">
                            <i class="bi bi-exclamation-circle"></i>
                            Estoque: ${produto.quantidade} / Mínimo: ${produto.estoque_minimo}
                        </small>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-${statusClass}">${statusText}</span>
                        <div class="btn-group mt-1" role="group">
                            <a href="/movimentacao/nova?produto=${produto.id}" class="btn btn-sm btn-success" title="Nova Entrada">
                                <i class="bi bi-plus"></i>
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });
        
        content += '</div>';
    }
    
    $('#alertas-content').html(content);
    
    // Atualizar badge no navbar
    $('#alertas-badge').text(data.total);
    if (data.total > 0) {
        $('#alertas-badge').show();
    } else {
        $('#alertas-badge').hide();
    }
}

// ========== SISTEMA DE NOTIFICAÇÕES ==========
function showNotification(title, message, type = 'info', duration = 4000) {
    type = type || 'info';
    var alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    var icon = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    }[type] || 'info-circle';
    
    var notification = $(`
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed animate-slide-in" 
             style="top: 20px; right: 20px; z-index: 9999; max-width: 350px;">
            <i class="bi bi-${icon}"></i>
            <strong>${title}</strong>
            ${message ? '<br>' + message : ''}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append(notification);
    
    // Auto-remove após duração especificada
    setTimeout(function() {
        notification.fadeOut(function() {
            $(this).remove();
        });
    }, duration);
}

// ========== VALIDAÇÃO DE FORMULÁRIOS ==========
function setupFormValidation() {
    // Validação de email em tempo real
    $('input[type="email"]').on('blur', function() {
        var email = $(this).val();
        var isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        
        if (email && !isValid) {
            $(this).addClass('is-invalid');
            $(this).siblings('.invalid-feedback').text('Email inválido');
        } else if (email && isValid) {
            $(this).removeClass('is-invalid').addClass('is-valid');
        }
    });
    
    // Validação de números
    $('input[type="number"]').on('input', function() {
        var value = $(this).val();
        var min = $(this).attr('min');
        var max = $(this).attr('max');
        
        if (min && value < min) {
            $(this).addClass('is-invalid');
            $(this).siblings('.invalid-feedback').text(`Valor mínimo: ${min}`);
        } else if (max && value > max) {
            $(this).addClass('is-invalid');
            $(this).siblings('.invalid-feedback').text(`Valor máximo: ${max}`);
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    
    // Confirmação de senha
    $('input[name="confirmar_senha"]').on('input', function() {
        var senha = $('input[name="senha"]').val();
        var confirmacao = $(this).val();
        
        if (confirmacao && senha !== confirmacao) {
            $(this).addClass('is-invalid');
            $(this).siblings('.invalid-feedback').text('Senhas não coincidem');
        } else if (confirmacao && senha === confirmacao) {
            $(this).removeClass('is-invalid').addClass('is-valid');
        }
    });
}

// ========== AÇÕES DE CONFIRMAÇÃO ==========
function setupConfirmActions() {
    // Confirmação para ações perigosas
    $('.btn-danger, .btn-outline-danger').not('.no-confirm').on('click', function(e) {
        if (!$(this).hasClass('confirmed')) {
            e.preventDefault();
            var message = $(this).data('confirm-message') || 'Tem certeza que deseja executar esta ação?';
            
            if (confirm(message)) {
                $(this).addClass('confirmed');
                $(this)[0].click();
            }
        }
    });
}

// ========== NAVEGAÇÃO POR TECLADO ==========
function setupKeyboardNavigation() {
    $(document).on('keydown', function(e) {
        // ESC para fechar modais
        if (e.key === 'Escape') {
            $('.modal.show').modal('hide');
        }
        
        // Ctrl+N para novo produto/movimentação
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            var currentPage = window.location.pathname;
            
            if (currentPage.includes('/produtos')) {
                window.location.href = '/produto/novo';
            } else if (currentPage.includes('/movimentacoes')) {
                window.location.href = '/movimentacao/nova';
            }
        }
        
        // Ctrl+F para focar na busca
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            $('input[name="search"], input[type="search"]').first().focus();
        }
    });
}

// ========== UTILITÁRIOS PARA FORMATAÇÃO ==========
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-BR');
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString('pt-BR');
}

// ========== FUNÇÕES PARA DATATABLES ==========
function initializeDataTable(selector, options = {}) {
    var defaultOptions = {
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json"
        },
        "responsive": true,
        "pageLength": 10,
        "lengthMenu": [10, 25, 50, 100],
        "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rtip',
        "order": []
    };
    
    return $(selector).DataTable($.extend(defaultOptions, options));
}

// ========== LOADING STATE ==========
function setLoadingState(element, loading = true) {
    var $element = $(element);
    
    if (loading) {
        $element.prop('disabled', true);
        var originalText = $element.text();
        $element.data('original-text', originalText);
        $element.html('<span class="spinner-border spinner-border-sm me-2"></span>Carregando...');
    } else {
        $element.prop('disabled', false);
        $element.html($element.data('original-text') || 'Concluído');
    }
}

// ========== AJAX HELPERS ==========
function makeAjaxRequest(url, method = 'GET', data = {}) {
    return $.ajax({
        url: url,
        method: method,
        data: data,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    });
}

// ========== SCROLL TO TOP ==========
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Mostrar botão de scroll to top quando necessário
$(window).scroll(function() {
    if ($(this).scrollTop() > 300) {
        if (!$('#scroll-top-btn').length) {
            $('body').append(`
                <button id="scroll-top-btn" class="btn btn-primary position-fixed" 
                        style="bottom: 20px; right: 20px; z-index: 1000; border-radius: 50%; width: 50px; height: 50px;"
                        onclick="scrollToTop()" title="Voltar ao topo">
                    <i class="bi bi-arrow-up"></i>
                </button>
            `);
        }
    } else {
        $('#scroll-top-btn').remove();
    }
});

// ========== CONSOLE LOG CUSTOMIZADO ==========
if (typeof console !== 'undefined') {
    console.log('%c🏪 Sistema de Controle de Estoque', 'color: #0d6efd; font-size: 16px; font-weight: bold;');
    console.log('%cDesenvolvido com Python/Flask', 'color: #198754; font-size: 12px;');
    console.log('%cVersão: 1.0.0', 'color: #6c757d; font-size: 10px;');
}

// ========== ERROR HANDLING GLOBAL ==========
window.addEventListener('error', function(e) {
    console.error('Erro JavaScript capturado:', e.error);
    // Em produção, você pode enviar erros para um serviço de monitoramento
});

// ========== ANIMAÇÃO DE SLIDE IN ==========
.animate-slide-in {
    animation: slideIn 0.5s ease-out;
}

// Adicionar CSS dinamicamente
$('<style>').text(`
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    .animate-slide-in {
        animation: slideIn 0.5s ease-out;
    }
`).appendTo('head');