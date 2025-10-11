import os
from app import create_app

# Criar a instância da aplicação para o Gunicorn
app = create_app(os.getenv('FLASK_CONFIG') or 'production')

# CONFIGURAÇÃO CRÍTICA PARA RENDER
# O Render precisa que a aplicação responda em 0.0.0.0:PORT
if os.getenv('FLASK_CONFIG') == 'production':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 RENDER: Aplicação configurada para porta {port}")
    print(f"🌐 RENDER: Binding configurado para 0.0.0.0:{port}")
    
    # Configurações críticas do Flask para Render
    app.config.update({
        'SERVER_NAME': None,  # Remove restrições de hostname
        'APPLICATION_ROOT': '/',  # Define root da aplicação
        'PREFERRED_URL_SCHEME': 'https',  # Render usa HTTPS
    })

# Para execução direta (desenvolvimento local)
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 DESENVOLVIMENTO: Iniciando aplicação em 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)