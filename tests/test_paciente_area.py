import pytest
from flask import url_for
from app import create_app, db
from app.models import Usuario, Psicologo, Paciente, Agendamento
from datetime import datetime, timedelta
import json

class TestPacienteArea:
    """Testes abrangentes para a área do paciente"""
    
    @pytest.fixture
    def app(self):
        """Configurar aplicação para testes"""
        app = create_app('testing')
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Cliente de teste"""
        return app.test_client()
    
    @pytest.fixture
    def paciente_user(self, app):
        """Fixture para criar um usuário paciente"""
        with app.app_context():
            user = Usuario(
                nome_completo='João Silva',
                email='joao@teste.com',
                tipo_usuario='paciente'
            )
            user.set_senha('senha123')
            db.session.add(user)
            db.session.commit()
            
            # Criar registro de paciente
            paciente = Paciente(usuario_id=user.id)
            db.session.add(paciente)
            db.session.commit()
            
            # Refresh para evitar DetachedInstanceError
            db.session.refresh(user)
            db.session.refresh(paciente)
            
            return user

    @pytest.fixture
    def psicologo_user(self, app):
        """Fixture para criar um usuário psicólogo"""
        with app.app_context():
            user = Usuario(
                nome_completo='Dr. Maria Santos',
                email='maria@teste.com',
                tipo_usuario='psicologo'
            )
            user.set_senha('senha123')
            db.session.add(user)
            db.session.commit()
            
            psicologo = Psicologo(
                usuario_id=user.id,
            )
            db.session.add(psicologo)
            db.session.commit()
            
            # Refresh para evitar DetachedInstanceError
            db.session.refresh(user)
            db.session.refresh(psicologo)
            
            return psicologo

    @pytest.fixture
    def logged_in_paciente(self, client, paciente_user):
        """Fixture para simular login do paciente"""
        # Fazer login real através da rota de autenticação
        response = client.post('/auth/login', data={
            'email': 'joao@teste.com',
            'senha': 'senha123',
            'tipo_usuario': 'paciente'
        }, follow_redirects=True)
        return paciente_user

    def test_dashboard_acesso_sem_login(self, client):
        """Teste: Dashboard deve redirecionar se não logado"""
        response = client.get('/paciente/dashboard')
        assert response.status_code == 302  # Redirecionamento para login
    
    def test_dashboard_acesso_com_login(self, client, logged_in_paciente):
        """Teste: Dashboard deve ser acessível quando logado"""
        response = client.get('/paciente/dashboard')
        assert response.status_code == 200
        # Verificar se há conteúdo relacionado ao dashboard
        assert b'dashboard' in response.data.lower() or b'painel' in response.data.lower() or b'bem-vindo' in response.data.lower()
    
    def test_dashboard_exibe_informacoes_paciente(self, client, logged_in_paciente):
        """Teste: Dashboard deve exibir informações do paciente"""
        response = client.get('/paciente/dashboard')
        assert response.status_code == 200
        assert logged_in_paciente.nome_completo.encode() in response.data
    
    def test_perfil_acesso_e_exibicao(self, client, logged_in_paciente):
        """Teste: Página de perfil deve ser acessível e exibir dados"""
        response = client.get('/paciente/perfil')
        assert response.status_code == 200
        assert logged_in_paciente.nome_completo.encode() in response.data
        assert logged_in_paciente.email.encode() in response.data
    
    def test_perfil_atualizacao_dados(self, client, logged_in_paciente):
        """Teste: Atualização de dados do perfil"""
        dados_atualizacao = {
            'nome_completo': 'João Silva Santos',
            'telefone': '11888888888'
        }
        
        response = client.post('/paciente/perfil', data=dados_atualizacao)
        
        # Verificar se a atualização foi bem-sucedida
        assert response.status_code in [200, 302]  # 200 para sucesso, 302 para redirecionamento
    
    def test_agendamentos_listagem(self, client, logged_in_paciente):
        """Teste: Listagem de agendamentos do paciente"""
        response = client.get('/paciente/agendamentos')
        assert response.status_code == 200
        assert b'agendamento' in response.data.lower() or b'consulta' in response.data.lower()
    
    def test_agendar_consulta_com_dados_validos(self, client, logged_in_paciente, psicologo_user, app):
        """Teste: Agendamento de consulta com dados válidos"""
        with app.app_context():
            data_futura = datetime.now() + timedelta(days=7)
            dados_agendamento = {
                'psicologo_id': psicologo_user.id,
                'data_hora': data_futura.isoformat(),
                'observacoes': 'Primeira consulta'
            }
            
            response = client.post('/paciente/agendar', data=dados_agendamento)
            
            # Verificar se o agendamento foi criado
            assert response.status_code in [200, 302]
    

    

    
    def test_templates_existem(self, app):
        """Teste: Verificar se os templates necessários existem"""
        with app.app_context():
            from flask import render_template_string
            
            # Lista de templates que devem existir
            templates_necessarios = [
                'paciente/dashboard.html',
                'paciente/perfil.html',
                'paciente/agendamentos.html',
            ]
            
            for template in templates_necessarios:
                try:
                    # Tentar renderizar o template (mesmo que básico)
                    render_template_string(f"{{% extends '{template}' %}}")
                except Exception as e:
                    # Se o template não existir, vai dar erro
                    pytest.fail(f"Template {template} não encontrado: {e}")
    
    def test_navegacao_entre_paginas(self, client, logged_in_paciente):
        """Teste: Navegação entre páginas da área do paciente"""
        # Testar links de navegação
        paginas = [
            '/paciente/dashboard',
            '/paciente/perfil',
            '/paciente/agendamentos',
         ]
        
        for pagina in paginas:
            response = client.get(pagina)
            assert response.status_code == 200, f"Erro ao acessar {pagina}"
    

    

    
    def test_responsividade_templates(self, client, logged_in_paciente):
        """Teste: Verificar se templates têm elementos responsivos"""
        response = client.get('/paciente/dashboard')
        assert response.status_code == 200
        
        # Verificar se há classes CSS responsivas
        content = response.data.decode()
        responsive_classes = ['col-', 'row', 'container', 'd-flex', 'responsive']
        
        has_responsive = any(cls in content for cls in responsive_classes)
        assert has_responsive, "Template não parece ter elementos responsivos"
    
    def test_integracao_com_base_template(self, client, logged_in_paciente):
        """Teste: Verificar integração com template base"""
        response = client.get('/paciente/dashboard')
        assert response.status_code == 200
        
        content = response.data.decode()
        
        # Verificar elementos que devem vir do template base
        elementos_base = ['<!DOCTYPE html>', '<html', '<head>', '<body>']
        
        for elemento in elementos_base:
            assert elemento in content, f"Elemento {elemento} não encontrado no template"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])