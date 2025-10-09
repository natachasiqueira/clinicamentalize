/**
 * Formatação automática de telefone (00) 00000-0000
 * Aplica máscara em todos os campos de telefone da aplicação
 */

document.addEventListener('DOMContentLoaded', function() {
    // Selecionar todos os campos de telefone
    const telefoneInputs = document.querySelectorAll('input[type="tel"], input[name="telefone"], input[id="telefone"], input[id="phone"]');
    
    telefoneInputs.forEach(function(input) {
        // Aplicar máscara durante a digitação
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); // Remove tudo que não é dígito
            
            if (value.length <= 11) {
                // Aplica a máscara (00) 00000-0000
                if (value.length <= 2) {
                    value = value.replace(/(\d{0,2})/, '($1');
                } else if (value.length <= 7) {
                    value = value.replace(/(\d{2})(\d{0,5})/, '($1) $2');
                } else {
                    value = value.replace(/(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
                }
            }
            
            e.target.value = value;
        });
        
        // Permitir apenas números e teclas de navegação
        input.addEventListener('keydown', function(e) {
            const allowedKeys = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab', 'Enter'];
            if (!allowedKeys.includes(e.key) && !/\d/.test(e.key)) {
                e.preventDefault();
            }
        });
        
        // Aplicar máscara no valor inicial se existir
        if (input.value) {
            let value = input.value.replace(/\D/g, '');
            if (value.length <= 11) {
                if (value.length <= 2) {
                    value = value.replace(/(\d{0,2})/, '($1');
                } else if (value.length <= 7) {
                    value = value.replace(/(\d{2})(\d{0,5})/, '($1) $2');
                } else {
                    value = value.replace(/(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
                }
                input.value = value;
            }
        }
        
        // Definir atributos para melhor UX
        input.setAttribute('maxlength', '15');
        input.setAttribute('inputmode', 'numeric');
        if (!input.placeholder) {
            input.setAttribute('placeholder', '(00) 00000-0000');
        }
    });
});