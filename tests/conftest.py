import pytest
import tempfile
import os
from app import create_app, db
from app.models import Usuario

@pytest.fixture(scope='session')
def app():
    """Fixture da aplicação Flask para testes - ISOLADA DO BANCO DE PRODUÇÃO"""
    # Cria um arquivo temporário para o banco de dados de teste
    db_fd, db_path = tempfile.mkstemp(suffix='.db', prefix='test_clinica_')
    
    # FORÇA o uso da configuração de teste
    app = create_app('testing')
    
    # GARANTE que está usando banco isolado
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        # Cria todas as tabelas no banco de teste
        db.create_all()
        yield app
        # Remove todas as tabelas após os testes
        db.drop_all()
    
    # Limpa o arquivo temporário
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Fixture do cliente de teste"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture do runner CLI"""
    return app.test_cli_runner()

@pytest.fixture
def admin_user(app):
    """Fixture para criar um usuário administrador de teste - APENAS NO BANCO DE TESTE"""
    with app.app_context():
        admin = Usuario(
            nome_completo='Admin Teste',
            email='admin@teste.com',
            telefone='(11) 99999-9999',
            tipo_usuario='admin'
        )
        admin.set_senha('senha123')
        db.session.add(admin)
        db.session.commit()
        return admin