import os
from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

# Criar a instância da aplicação para o Gunicorn
app = create_app(os.getenv('FLASK_CONFIG') or 'production')

def init_database_if_needed():
    """Inicializa o banco de dados se necessário"""
    with app.app_context():
        try:
            # Tenta fazer uma query simples para verificar se as tabelas existem
            Usuario.query.first()
            print("✓ Banco de dados já inicializado")
        except Exception as e:
            print("⚠️ Banco de dados não inicializado. Criando tabelas...")
            try:
                # Cria todas as tabelas
                db.create_all()
                print("✓ Tabelas criadas com sucesso!")
                
                # Verifica se já existe um usuário admin
                admin_email = 'admin@clinicamentalize.com.br'
                admin_user = Usuario.query.filter_by(email=admin_email).first()
                
                if not admin_user:
                    print("Criando usuário administrador padrão...")
                    
                    # Senha padrão do .env
                    default_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')
                    
                    new_admin = Usuario(
                        nome_completo='Administrativo',
                        tipo_usuario='admin',
                        email=admin_email,
                        telefone='(11) 96331-3561',
                        senha_hash=generate_password_hash(default_password)
                    )
                    
                    db.session.add(new_admin)
                    db.session.commit()
                    
                    print("✓ Usuário administrador criado com sucesso!")
                    print(f"  Email: {admin_email}")
                    print(f"  Senha: {default_password}")
                else:
                    print("✓ Usuário administrador já existe")
                    
            except Exception as init_error:
                print(f"❌ Erro ao inicializar banco: {init_error}")

# Inicializar banco se necessário (apenas em produção)
if os.getenv('FLASK_CONFIG') == 'production':
    init_database_if_needed()

if __name__ == "__main__":
    app.run()