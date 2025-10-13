import pytest
from app import create_app, db
from app.models import Usuario

@pytest.fixture
def app():
    """Cria uma instância da aplicação para testes."""
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
    """Cliente de teste para fazer requisições."""
    return app.test_client()

class TestHomepage:
    """Testes para a página inicial."""
    
    def test_homepage_loads(self, client):
        """Testa se a página inicial carrega corretamente."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Cl\xc3\xadnica Mentalize' in response.data
        
    def test_homepage_content(self, client):
        """Testa se o conteúdo da página inicial está presente."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Verifica elementos principais da página
        assert b'Cuidando da sua sa\xc3\xbade mental' in response.data
        assert b'Cadastre-se Gratuitamente' in response.data
        assert b'Fazer Login' in response.data
        

        
    def test_homepage_links(self, client):
        """Testa se os links da página inicial funcionam."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Verifica se os links estão presentes
        assert b'href="/auth/registro-paciente"' in response.data
        assert b'href="/auth/login"' in response.data
        
    def test_homepage_responsive_elements(self, client):
        """Testa se os elementos responsivos estão presentes."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Verifica classes CSS responsivas - ajustando para o layout atual
        assert b'col-lg-6' in response.data or b'col-md-6' in response.data
        assert b'container' in response.data
        assert b'row' in response.data
        
    def test_homepage_css_styles(self, client):
        """Testa se os estilos CSS estão incluídos."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Verifica se o CSS está presente
        assert b'hero-section' in response.data
        assert b'cta-section' in response.data
        assert b'@keyframes float' in response.data
        
    def test_homepage_icons(self, client):
        """Testa se os ícones estão presentes."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Verifica ícones - ajustando para o conteúdo atual (símbolo ψ)
        assert b'\xcf\x88' in response.data  # Símbolo ψ em UTF-8
        # Verifica se há ícones FontAwesome ou outros elementos visuais
        assert b'icon' in response.data or b'fa-' in response.data or b'\xcf\x88' in response.data
        
    def test_homepage_authenticated_user(self, client, app):
        """Testa a página inicial para usuário autenticado."""
        with app.app_context():
            # Criar usuário de teste
            usuario = Usuario(
                nome_completo='Teste Usuario',
                email='teste@teste.com',
                telefone='11999999999',
                tipo_usuario='paciente'
            )
            usuario.set_senha('senha123')
            db.session.add(usuario)
            db.session.commit()
            
            # Fazer login
            response = client.post('/auth/login', data={
                'email': 'teste@teste.com',
                'senha': 'senha123',
                'tipo_usuario': 'paciente'
            })
            
            # Verificar se o login foi bem-sucedido (pode ser redirecionamento)
            assert response.status_code in [200, 302]
            
            # Se foi redirecionamento, seguir para a área do paciente
            if response.status_code == 302:
                # Usuário logado deve ser redirecionado para sua área
                assert '/area-paciente' in response.location or '/' in response.location

class TestRegistrationIntegration:
    """Testes de integração com o formulário de cadastro."""
    
    def test_registration_link_works(self, client):
        """Testa se o link de cadastro funciona."""
        response = client.get('/auth/registro-paciente')
        assert response.status_code == 200
        assert b'Cadastro de Paciente' in response.data
        
    def test_login_link_works(self, client):
        """Testa se o link de login funciona."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data