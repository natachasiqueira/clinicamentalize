#!/usr/bin/env python3
"""
Script para inicialização segura do banco de dados
Execute este script APENAS UMA VEZ após o primeiro deploy
"""
import os
import sys
from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializa o banco de dados de forma segura"""
    
    # Criar aplicação
    app = create_app(os.getenv('FLASK_CONFIG') or 'production')
    
    with app.app_context():
        try:
            print("🔧 Iniciando inicialização do banco de dados...")
            
            # Verificar se já existe usuário admin primeiro (evita recriar)
            admin_email = 'admin@clinicamentalize.com.br'
            try:
                admin_user = Usuario.query.filter_by(email=admin_email).first()
                if admin_user:
                    print("ℹ️ Usuário administrador já existe:")
                    print(f"   Email: {admin_user.email}")
                    print(f"   ID: {admin_user.id}")
                    print(f"   Ativo: {admin_user.ativo}")
                    print("✅ Banco já inicializado - pulando criação")
                    return True
            except Exception as query_error:
                # Se der erro na query, provavelmente as tabelas não existem
                print(f"ℹ️ Tabelas não existem ainda: {query_error}")
            
            # Criar todas as tabelas
            print("📋 Criando tabelas...")
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            
            # Criar usuário administrador
            print("👤 Criando usuário administrador...")
            admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
            
            new_admin = Usuario(
                nome_completo='Administrador Sistema',
                tipo_usuario='admin',
                email=admin_email,
                telefone='(11) 96331-3561',
                senha_hash=generate_password_hash(admin_password),
                ativo=True
            )
            
            # Adicionar e fazer commit com tratamento de erro
            db.session.add(new_admin)
            db.session.commit()
            
            print("✅ Usuário administrador criado com sucesso!")
            print(f"   Email: {admin_email}")
            print(f"   Senha: {admin_password}")
            print("⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
            
            # Verificar se foi criado corretamente
            created_admin = Usuario.query.filter_by(email=admin_email).first()
            if created_admin:
                print(f"✅ Verificação: Admin encontrado no banco (ID: {created_admin.id})")
                return True
            else:
                print("❌ Erro: Admin não foi encontrado após criação!")
                return False
                
        except Exception as e:
            print(f"❌ Erro durante inicialização: {e}")
            try:
                db.session.rollback()
                print("🔄 Rollback executado")
            except Exception as rollback_error:
                print(f"❌ Erro no rollback: {rollback_error}")
            return False

def check_database_connection():
    """Verifica se a conexão com o banco está funcionando"""
    app = create_app(os.getenv('FLASK_CONFIG') or 'production')
    
    with app.app_context():
        try:
            # Tenta uma query simples usando SQLAlchemy 2.0+ syntax
            from sqlalchemy import text
            with db.engine.connect() as connection:
                result = connection.execute(text('SELECT 1'))
                result.close()
            print("✅ Conexão com banco de dados OK")
            return True
        except Exception as e:
            print(f"❌ Erro de conexão com banco: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Script de Inicialização do Banco - Clínica Mentalize")
    print("=" * 50)
    
    # Verificar conexão primeiro
    if not check_database_connection():
        print("❌ Falha na conexão com banco. Verifique a DATABASE_URL")
        sys.exit(1)
    
    # Inicializar banco
    if init_database():
        print("=" * 50)
        print("✅ Inicialização concluída com sucesso!")
        print("🌐 Sua aplicação está pronta para uso")
    else:
        print("=" * 50)
        print("❌ Falha na inicialização")
        sys.exit(1)