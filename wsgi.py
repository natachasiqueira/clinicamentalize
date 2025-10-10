import os
from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

# Criar a instância da aplicação para o Gunicorn
app = create_app(os.getenv('FLASK_CONFIG') or 'production')

# Configurar porta para Render
if os.getenv('FLASK_CONFIG') == 'production':
    # Garantir que a aplicação use a porta correta no Render
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Aplicação configurada para porta: {port}")
    print(f"🌐 Binding para: 0.0.0.0:{port}")
    
    # Configurar o Flask para fazer bind correto
    app.config['SERVER_NAME'] = None  # Remove server name restrictions
    app.config['APPLICATION_ROOT'] = '/'

def init_database_if_needed():
    """Inicializa o banco de dados se necessário"""
    with app.app_context():
        try:
            # Tenta fazer uma query simples para verificar se as tabelas existem
            Usuario.query.first()
            print("✓ Banco de dados já inicializado")
        except Exception as e:
            print("⚠️ Banco de dados não inicializado. Criando tabelas...")
            
            # Rollback da transação atual em caso de erro
            db.session.rollback()
            
            try:
                # Cria todas as tabelas
                db.create_all()
                print("✓ Tabelas criadas com sucesso!")
                
                # Verifica se já existe um usuário admin
                admin_email = 'admin@clinicamentalize.com.br'
                
                try:
                    admin_user = Usuario.query.filter_by(email=admin_email, tipo_usuario='admin').first()
                except Exception:
                    # Se der erro na query, assume que não existe
                    admin_user = None
                
                if not admin_user:
                    print("Criando usuário administrador padrão...")
                    
                    # Senha padrão do .env
                    default_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')
                    
                    new_admin = Usuario(
                        nome_completo='Administrativo',
                        tipo_usuario='admin',
                        email=admin_email,
                        telefone='(11) 96331-3561',
                        ativo=True
                    )
                    new_admin.set_senha(default_password)
                    
                    db.session.add(new_admin)
                    db.session.commit()
                    
                    print("✓ Usuário administrador criado com sucesso!")
                    print(f"  Email: {admin_email}")
                    print(f"  Senha: {default_password}")
                    print(f"  Tipo: admin")
                    print(f"  Ativo: True")
                    
                    # Verificação adicional
                    created_admin = Usuario.query.filter_by(email=admin_email, tipo_usuario='admin').first()
                    if created_admin:
                        print("✓ Verificação: Admin criado e encontrado no banco!")
                        print(f"  ID: {created_admin.id}")
                        print(f"  Hash da senha: {created_admin.senha_hash[:20]}...")
                    else:
                        print("❌ Erro: Admin não foi encontrado após criação!")
                else:
                    print("✓ Usuário administrador já existe")
                    print(f"  ID: {admin_user.id}")
                    print(f"  Email: {admin_user.email}")
                    print(f"  Tipo: {admin_user.tipo_usuario}")
                    print(f"  Ativo: {admin_user.ativo}")
                    
            except Exception as init_error:
                print(f"❌ Erro ao inicializar banco: {init_error}")
                db.session.rollback()

# Inicializar banco se necessário (apenas em produção)
if os.getenv('FLASK_CONFIG') == 'production':
    init_database_if_needed()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))  # Usar 10000 como padrão do Render
    print(f"🚀 Iniciando aplicação em 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)