import os
from app import create_app, db
from app.models import Usuario, Psicologo, Paciente, Agendamento, Prontuario, Sessao, HorarioAtendimento

# Criação da aplicação
print("🚀 RENDER: Iniciando criação da aplicação...")
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
print("✅ RENDER: Aplicação criada com sucesso!")

@app.shell_context_processor
def make_shell_context():
    """Contexto do shell para facilitar testes e desenvolvimento"""
    return {
        'db': db,
        'Usuario': Usuario,
        'Psicologo': Psicologo,
        'Paciente': Paciente,
        'Agendamento': Agendamento,
        'Prontuario': Prontuario,
        'Sessao': Sessao,
        'HorarioAtendimento': HorarioAtendimento
    }

@app.cli.command()
def init_db():
    """Inicializa o banco de dados"""
    db.create_all()
    print('Banco de dados inicializado.')

@app.cli.command()
def init_default_users():
    """Inicializa usuários padrão do sistema"""
    from werkzeug.security import generate_password_hash
    
    # Dados dos usuários padrão
    default_users = [
        {
            'nome_completo': 'Administrativo',
            'tipo_usuario': 'admin',
            'email': 'admin@clinicamentalize.com.br',
            'telefone': '(11) 96331-3561',
            'senha': os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
        },
    ]
    
    for user_data in default_users:
        # Verifica se o usuário já existe
        existing_user = Usuario.query.filter_by(email=user_data['email']).first()
        
        if not existing_user:
            # Cria o usuário
            new_user = Usuario(
                nome_completo=user_data['nome_completo'],
                tipo_usuario=user_data['tipo_usuario'],
                email=user_data['email'],
                telefone=user_data['telefone'],
                senha_hash=generate_password_hash(user_data['senha'])
            )
            
            db.session.add(new_user)
            print(f"Usuário criado: {user_data['nome_completo']} ({user_data['email']})")
        else:
            print(f"Usuário já existe: {user_data['nome_completo']} ({user_data['email']})")
    
    try:
        db.session.commit()
        print("Usuários padrão inicializados com sucesso!")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar usuários padrão: {e}")

# Inicialização automática dos usuários padrão na primeira execução
def initialize_default_users():
    """Inicializa usuários padrão automaticamente na primeira execução"""
    try:
        print("DEBUG: Iniciando initialize_default_users()")
        # Verifica se já existem usuários no sistema
        user_count = Usuario.query.count()
        print(f"DEBUG: user_count = {user_count}")
        if user_count == 0:
            print("DEBUG: user_count é 0, criando usuários padrão...")
            from werkzeug.security import generate_password_hash
            
            # Dados dos usuários padrão
            default_users = [
                {
                    'nome_completo': 'Administrativo',
                    'tipo_usuario': 'admin',
                    'email': 'admin@clinicamentalize.com.br',
                    'telefone': '(11) 96331-3561',
                    'senha': os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
                }
            ]
            
            for user_data in default_users:
                new_user = Usuario(
                    nome_completo=user_data['nome_completo'],
                    tipo_usuario=user_data['tipo_usuario'],
                    email=user_data['email'],
                    telefone=user_data['telefone'],
                    senha_hash=generate_password_hash(user_data['senha'])
                )
                db.session.add(new_user)
                print(f"DEBUG: Adicionado usuário {user_data['email']} à sessão.")
            
            db.session.commit()
            print("Usuários padrão criados automaticamente!")
        else:
            print("DEBUG: Já existem usuários no banco de dados, pulando a criação de usuários padrão.")
    except Exception as e:
        print(f"Erro na inicialização automática: {e}")

# Chama a inicialização na primeira execução APENAS em desenvolvimento
# Em produção, o init_db.py cuida da inicialização
if os.getenv('FLASK_CONFIG') != 'production':
    with app.app_context():
        db.create_all()
        # Garante que o usuário admin seja criado se não existir
        from app.models import Usuario
        from werkzeug.security import generate_password_hash
        
        admin_email = 'admin@clinicamentalize.com.br'
        admin_user = Usuario.query.filter_by(email=admin_email).first()
        
        if not admin_user:
            print("Criando usuário administrador padrão...")
            new_admin = Usuario(
                nome_completo='Administrativo',
                tipo_usuario='admin',
                email=admin_email,
                telefone='(11) 96331-3561',
                senha_hash=generate_password_hash(os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123'))
            )
            db.session.add(new_admin)
            db.session.commit()
            print("Usuário administrador padrão criado com sucesso!")
        else:
            print("Usuário administrador já existe.")

if __name__ == '__main__':
    # Em produção, o gunicorn será usado ao invés do servidor de desenvolvimento
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug_mode)