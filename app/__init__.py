from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import config

# Inicialização das extensões
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name='default'):
    """Factory function para criar a aplicação Flask"""
    print(f"🔧 RENDER: Iniciando create_app com config: {config_name}")
    app = Flask(__name__)
    print("📦 RENDER: Flask app criada")
    
    # Configuração da aplicação
    app.config.from_object(config[config_name])
    print("⚙️ RENDER: Configurações carregadas")
    
    # Configuração específica para Render
    if config_name == 'production':
        # Garantir que a aplicação aceite conexões de qualquer IP
        app.config['SERVER_NAME'] = None
        # Configurar porta do Render
        import os
        port = int(os.environ.get('PORT', 10000))
        print(f"🌐 Flask configurado para produção na porta: {port}")
        print(f"🚀 RENDER: Aplicação configurada para porta {port}")
        print(f"🌐 RENDER: Binding configurado para 0.0.0.0:{port}")
    
    # Inicialização das extensões
    print("🔌 RENDER: Inicializando extensões...")
    db.init_app(app)
    print("🗄️ RENDER: SQLAlchemy inicializado")
    login_manager.init_app(app)
    print("🔐 RENDER: LoginManager inicializado")
    migrate.init_app(app, db)
    print("🔄 RENDER: Migrate inicializado")
    CORS(app)
    print("🌐 RENDER: CORS inicializado")
    
    # Configuração do Flask-Login
    print("🔑 RENDER: Configurando Flask-Login...")
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    print("✅ RENDER: Flask-Login configurado")
    
    # Registro dos blueprints
    print("📋 RENDER: Registrando blueprints...")
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    print("🔐 RENDER: Blueprint auth registrado")
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    print("🔌 RENDER: Blueprint api registrado")
# Registrar blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    print("🏠 RENDER: Blueprint main registrado")
    
    from app.paciente import bp as paciente_bp
    app.register_blueprint(paciente_bp, url_prefix='/paciente')
    print("👤 RENDER: Blueprint paciente registrado")
    
    from app.psicologo import bp as psicologo_bp
    app.register_blueprint(psicologo_bp, url_prefix='/psicologo')
    print("👨‍⚕️ RENDER: Blueprint psicologo registrado")
    
    from app.admin import admin as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    print("👑 RENDER: Blueprint admin registrado")
    
    # Importação dos modelos para que sejam reconhecidos pelo SQLAlchemy
    print("📊 RENDER: Importando modelos...")
    from app import models
    print("✅ RENDER: Modelos importados")
    
    # Filtros personalizados para tradução
    print("🎨 RENDER: Configurando filtros personalizados...")
    @app.template_filter('dia_semana_pt')
    def dia_semana_pt(data):
        """Converte dia da semana para português"""
        dias = {
            'Monday': 'Segunda-feira',
            'Tuesday': 'Terça-feira', 
            'Wednesday': 'Quarta-feira',
            'Thursday': 'Quinta-feira',
            'Friday': 'Sexta-feira',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        return dias.get(data.strftime('%A'), data.strftime('%A'))
    
    @app.template_filter('mes_pt')
    def mes_pt(data):
        """Converte mês para português"""
        meses = {
            'January': 'Janeiro',
            'February': 'Fevereiro',
            'March': 'Março',
            'April': 'Abril',
            'May': 'Maio',
            'June': 'Junho',
            'July': 'Julho',
            'August': 'Agosto',
            'September': 'Setembro',
            'October': 'Outubro',
            'November': 'Novembro',
            'December': 'Dezembro'
        }
        return meses.get(data.strftime('%B'), data.strftime('%B'))
    
    print("🎉 RENDER: Aplicação Flask criada com sucesso!")
    return app