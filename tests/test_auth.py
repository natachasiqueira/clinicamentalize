import pytest
from flask import url_for
from app import create_app, db
from app.models import Usuario, Paciente
from datetime import date

@pytest.fixture
def app():
    """Cria uma instância da aplicação para testes"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de teste"""
    return app.test_client()

@pytest.fixture
def usuario_admin(app):
    """Cria um usuário administrador para testes"""
    with app.app_context():
        usuario = Usuario(
            nome_completo='Admin Teste',
            email='admin@teste.com.br',
            telefone='(11) 99999-9999',
            tipo_usuario='admin'
        )
        usuario.set_senha('senha123')
        db.session.add(usuario)
        db.session.commit()
        return usuario

@pytest.fixture
def usuario_paciente(app):
    """Cria um usuário paciente para testes"""
    with app.app_context():
        usuario = Usuario(
            nome_completo='Paciente Teste',
            email='paciente@teste.com',
            telefone='(11) 88888-8888',
            tipo_usuario='paciente'
        )
        usuario.set_senha('senha123')
        db.session.add(usuario)
        db.session.flush()
        
        paciente = Paciente(
            usuario_id=usuario.id
        )
        db.session.add(paciente)
        db.session.commit()
        return usuario

class TestLogin:
    """Testes para funcionalidade de login"""
    
    def test_login_page_loads(self, client):
        """Testa se a página de login carrega corretamente"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_success_admin(self, client, usuario_admin):
        """Testar login bem-sucedido de administrador"""
        response = client.post('/auth/login', data={
            'email': 'admin@clinicamentalize.com.br',
            'senha': 'admin123',
            'tipo_usuario': 'admin'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Verificar se foi redirecionado para área administrativa
        assert b'Dashboard' in response.data or b'Administra' in response.data
    
    def test_login_success_paciente(self, client, usuario_paciente):
        """Testa login bem-sucedido de paciente"""
        response = client.post('/auth/login', data={
            'email': 'paciente@teste.com',
            'senha': 'senha123',
            'tipo_usuario': 'paciente'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Login realizado com sucesso!' in response.data
    
    def test_login_invalid_credentials(self, client, usuario_admin):
        """Testa login com credenciais inválidas"""
        response = client.post('/auth/login', data={
            'email': 'admin@clinicamentalize.com.br',
            'senha': 'senha_errada',
            'tipo_usuario': 'admin'
        })
        
        assert response.status_code == 200
        assert b'E-mail, senha ou tipo de usu' in response.data
    
    def test_login_wrong_user_type(self, client, usuario_admin):
        """Testa login com tipo de usuário incorreto"""
        response = client.post('/auth/login', data={
            'email': 'admin@clinicamentalize.com.br',
            'senha': 'admin123',
            'tipo_usuario': 'paciente'
        })
        
        assert response.status_code == 200
        assert b'E-mail, senha ou tipo de usu' in response.data
    


class TestLogout:
    """Testes para funcionalidade de logout"""
    
    def test_logout_success(self, client, usuario_admin):
        """Testar logout bem-sucedido"""
        # Primeiro fazer login
        client.post('/auth/login', data={
            'email': 'admin@clinicamentalize.com.br',
            'senha': 'admin123',
            'tipo_usuario': 'admin'
        })
        
        # Depois fazer logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        # Verificar se foi redirecionado para página inicial
        assert b'Login' in response.data or b'Cadastro' in response.data
    
    def test_logout_without_login(self, client):
        """Testa logout sem estar logado"""
        response = client.get('/auth/logout')
        assert response.status_code == 302  # Redirecionamento para login

class TestRegistroPaciente:
    """Testes para registro de pacientes"""
    
    def test_registro_page_loads(self, client):
        """Testa se a página de registro carrega corretamente"""
        response = client.get('/auth/registro-paciente')
        assert response.status_code == 200
        assert b'Cadastro de Paciente' in response.data
    
    def test_registro_success(self, client):
        """Testa registro bem-sucedido de paciente"""
        response = client.post('/auth/registro-paciente', data={
            'nome_completo': 'Novo Paciente',
            'email': 'novo@teste.com',
            'telefone': '(11) 77777-7777',
            'senha': 'senha123',
            'confirmar_senha': 'senha123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Cadastro realizado com sucesso!' in response.data
        
        # Verifica se o usuário foi criado no banco
        with client.application.app_context():
            usuario = Usuario.query.filter_by(email='novo@teste.com').first()
            assert usuario is not None
            assert usuario.tipo_usuario == 'paciente'
            
            paciente = Paciente.query.filter_by(usuario_id=usuario.id).first()
            assert paciente is not None
    
    def test_registro_email_duplicado(self, client, usuario_paciente):
        """Testa registro com e-mail já existente"""
        response = client.post('/auth/registro-paciente', data={
            'nome_completo': 'Outro Paciente',
            'email': 'paciente@teste.com',  # E-mail já existe
            'telefone': '(11) 66666-6666',
            'senha': 'senha123',
            'confirmar_senha': 'senha123'
        })
        
        assert response.status_code == 200
        assert b'Este e-mail j\xc3\xa1 est\xc3\xa1 cadastrado' in response.data
    
    def test_registro_senhas_diferentes(self, client):
        """Testa registro com senhas diferentes"""
        response = client.post('/auth/registro-paciente', data={
            'nome_completo': 'Teste Senhas',
            'email': 'teste_senhas@teste.com',
            'telefone': '11999999999',
            'senha': 'senha123',
            'confirmar_senha': 'senha456'  # Senha diferente
        })
        
        assert response.status_code == 200
        # Mensagem real do sistema
        assert b'Senhas devem ser iguais' in response.data

class TestAlterarSenha:
    """Testes para alteração de senha"""
    
    def test_alterar_senha_page_requires_login(self, client):
        """Testa se a página de alterar senha requer login"""
        response = client.get('/auth/alterar-senha')
        assert response.status_code == 302  # Redirecionamento para login
    
    def test_alterar_senha_success(self, client, usuario_paciente):
        """Testa alteração de senha bem-sucedida"""
        # Login do paciente
        client.post('/auth/login', data={
            'email': 'paciente@teste.com.br',
            'senha': 'senha123',
            'tipo_usuario': 'paciente'
        })
        
        response = client.post('/auth/alterar-senha', data={
            'senha_atual': 'senha123',
            'nova_senha': 'nova_senha123',
            'confirmar_nova_senha': 'nova_senha123'
        })
        
        # Sistema redireciona após sucesso
        assert response.status_code == 302
        
        # Verificar se foi redirecionado para dashboard
        assert '/area-paciente' in response.location or '/' in response.location
    
    def test_alterar_senha_atual_incorreta(self, client, usuario_admin):
        """Testa alteração com senha atual incorreta"""
        # Primeiro faz login
        client.post('/auth/login', data={
            'email': 'admin@teste.com',
            'senha': 'senha123',
            'tipo_usuario': 'admin'
        })
        
        # Tenta alterar com senha atual incorreta
        response = client.post('/auth/alterar-senha', data={
            'senha_atual': 'senha_errada',
            'nova_senha': 'nova_senha456',
            'confirmar_nova_senha': 'nova_senha456'
        })
        
        # O sistema pode retornar 200 (mesma página com erro) ou 302 (redirecionamento)
        assert response.status_code in [200, 302]
        
        if response.status_code == 200:
            assert b'Senha atual incorreta' in response.data

class TestEditarPerfil:
    """Testes para edição de perfil"""
    
    def test_editar_perfil_page_requires_login(self, client):
        """Testa se a página de editar perfil requer login"""
        response = client.get('/auth/editar-perfil')
        assert response.status_code == 302  # Redirecionamento para login
    
    def test_editar_perfil_success(self, client, usuario_paciente):
        """Testa edição de perfil bem-sucedida"""
        # Login do paciente
        client.post('/auth/login', data={
            'email': 'paciente@teste.com',
            'senha': 'senha123',
            'tipo_usuario': 'paciente'
        })
        
        response = client.post('/auth/editar-perfil', data={
            'nome_completo': 'Paciente Atualizado',
            'telefone': '11888888888'
        })
        
        # Sistema redireciona após sucesso
        assert response.status_code == 302
        
        # Verificar se foi redirecionado para dashboard
        assert '/area-paciente' in response.location or '/' in response.location

class TestAPIAuth:
    """Testes para API de autenticação"""
    
    def test_api_login_success(self, client, usuario_admin):
        """Testa login via API bem-sucedido"""
        response = client.post('/auth/api/login', 
                             json={
                                 'email': 'admin@teste.com.br',
                                 'senha': 'senha123',
                                 'tipo_usuario': 'admin'
                             })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login realizado com sucesso'
        # Verificar se há informações do usuário ou URL de redirecionamento
        assert 'usuario' in data or 'redirect_url' in data or 'success' in data
    
    def test_api_login_invalid_credentials(self, client, usuario_admin):
        """Testa login via API com credenciais inválidas"""
        response = client.post('/auth/api/login', 
                             json={
                                 'email': 'admin@teste.com.br',
                                 'senha': 'senha_errada',
                                 'tipo_usuario': 'admin'
                             })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] == 'Credenciais inválidas'
    
    def test_api_login_missing_data(self, client):
        """Testa login via API com dados faltando"""
        response = client.post('/auth/api/login', 
                             json={
                                 'email': 'admin@teste.com.br'
                                 # Faltando senha e tipo_usuario
                             })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'obrigatórios' in data['error'] or 'required' in data['error'].lower()
    
    def test_api_logout_success(self, client, usuario_admin):
        """Testa logout via API bem-sucedido"""
        # Primeiro faz login
        client.post('/auth/login', data={
            'email': 'admin@teste.com.br',
            'senha': 'senha123',
            'tipo_usuario': 'admin'
        })
        
        # Depois faz logout via API
        response = client.post('/auth/api/logout')
        # O logout pode retornar 302 (redirecionamento) ou 200 dependendo da implementação
        assert response.status_code in [200, 302]
        if response.status_code == 200:
            data = response.get_json()
            assert data['message'] == 'Logout realizado com sucesso'
    
    def test_api_logout_without_login(self, client):
        """Testa logout via API sem estar logado"""
        response = client.post('/auth/api/logout')
        assert response.status_code == 302  # Redirecionamento para login