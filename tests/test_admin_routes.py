import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from app.models import Usuario, Admin, Paciente, Psicologo, Agendamento, db
from datetime import datetime, timedelta
import pytz


class TestAdminRoutes:
    """Testes para as rotas administrativas"""

    @pytest.fixture
    def admin_user(self, app):
        """Cria um usuário administrador para testes"""
        with app.app_context():
            admin_usuario = Usuario(
                nome_completo='Admin Teste',
                email='admin@teste.com',
                telefone='11999999999',
                senha_hash=generate_password_hash('senha123'),
                tipo_usuario='admin'
            )
            db.session.add(admin_usuario)
            db.session.commit()
            
            admin = Admin(usuario_id=admin_usuario.id)
            db.session.add(admin)
            db.session.commit()
            
            # Refresh para evitar DetachedInstanceError
            db.session.refresh(admin_usuario)
            db.session.refresh(admin)
            
            return admin_usuario

    @pytest.fixture
    def sample_paciente(self, app):
        """Cria um paciente para testes"""
        with app.app_context():
            paciente_usuario = Usuario(
                nome_completo='Paciente Teste',
                email='paciente@teste.com',
                telefone='11888888888',
                senha_hash=generate_password_hash('senha123'),
                tipo_usuario='paciente'
            )
            db.session.add(paciente_usuario)
            db.session.commit()
            
            paciente = Paciente(
                usuario_id=paciente_usuario.id
            )
            db.session.add(paciente)
            db.session.commit()
            
            # Refresh para evitar DetachedInstanceError
            db.session.refresh(paciente_usuario)
            db.session.refresh(paciente)
            
            return paciente

    @pytest.fixture
    def sample_psicologo(self, app):
        """Cria um psicólogo para testes"""
        with app.app_context():
            psicologo_usuario = Usuario(
                nome_completo='Psicólogo Teste',
                email='psicologo@teste.com',
                telefone='11777777777',
                senha_hash=generate_password_hash('senha123'),
                tipo_usuario='psicologo'
            )
            db.session.add(psicologo_usuario)
            db.session.commit()
            
            psicologo = Psicologo(
                usuario_id=psicologo_usuario.id
            )
            db.session.add(psicologo)
            db.session.commit()
            
            # Refresh para evitar DetachedInstanceError
            db.session.refresh(psicologo_usuario)
            db.session.refresh(psicologo)
            
            return psicologo

    @pytest.fixture
    def sample_agendamentos(self, app, sample_paciente, sample_psicologo):
        """Cria agendamentos de exemplo para testes"""
        with app.app_context():
            agora_utc = datetime.now(pytz.utc)
            agendamentos = []
            
            # Criar alguns agendamentos de exemplo para os últimos 6 meses
            for i in range(10):
                data_agendamento = agora_utc - timedelta(days=i*15)  # Espaçados de 15 em 15 dias
                agendamento = Agendamento(
                    paciente_id=sample_paciente.id,
                    psicologo_id=sample_psicologo.id,
                    data_hora=data_agendamento,
                    status='realizado' if i % 2 == 0 else 'confirmado',
                    observacoes=f'Agendamento teste {i+1}'
                )
                db.session.add(agendamento)
                agendamentos.append(agendamento)
            
            db.session.commit()
            
            # Refresh para evitar DetachedInstanceError
            for agendamento in agendamentos:
                db.session.refresh(agendamento)
            
            return agendamentos

    def test_admin_perfil_get(self, client, admin_user):
        """Testa o acesso à página de perfil do admin"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        response = client.get(url_for('admin.perfil'))
        assert response.status_code == 200
        assert b'Meu Perfil' in response.data

    def test_admin_perfil_post_success(self, client, admin_user, sample_agendamentos):
        """Testa a atualização bem-sucedida do perfil do admin"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        data = {
            'nome_completo': 'Admin Atualizado',
            'email': 'admin_novo@teste.com',
            'telefone': '11555555555'
        }
        
        response = client.post(url_for('admin.perfil'), data=data, follow_redirects=True)
        assert response.status_code == 200

    def test_admin_perfil_post_with_password(self, client, admin_user, sample_agendamentos):
        """Testa a atualização do perfil com mudança de senha"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        data = {
            'nome_completo': 'Admin Teste',
            'email': 'admin@teste.com',
            'telefone': '11999999999',
            'nova_senha': 'novasenha123',
            'confirmar_senha': 'novasenha123'
        }
        
        response = client.post(url_for('admin.perfil'), data=data, follow_redirects=True)
        assert response.status_code == 200

    def test_admin_perfil_password_mismatch(self, client, admin_user):
        """Testa erro quando senhas não coincidem"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        data = {
            'nome_completo': 'Admin Teste',
            'email': 'admin@teste.com',
            'telefone': '11999999999',
            'nova_senha': 'senha123',
            'confirmar_senha': 'senha456'
        }
        
        response = client.post(url_for('admin.perfil'), data=data)
        assert response.status_code == 200
        assert 'As senhas não coincidem.' in response.get_data(as_text=True)

    def test_admin_perfil_short_password(self, client, admin_user):
        """Testa erro quando senha é muito curta"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        data = {
            'nome_completo': 'Admin Teste',
            'email': 'admin@teste.com',
            'telefone': '11999999999',
            'nova_senha': '123',
            'confirmar_senha': '123'
        }
        
        response = client.post(url_for('admin.perfil'), data=data)
        assert response.status_code == 200
        assert 'A senha deve ter pelo menos 6 caracteres.' in response.get_data(as_text=True)

    def test_listar_pacientes(self, client, admin_user, sample_paciente):
        """Testa a listagem de pacientes"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        response = client.get(url_for('admin.listar_pacientes'))
        assert response.status_code == 200
        assert 'Paciente Teste' in response.get_data(as_text=True)

    def test_listar_psicologos(self, client, admin_user, sample_psicologo):
        """Testa a listagem de psicólogos"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        response = client.get(url_for('admin.listar_psicologos'))
        assert response.status_code == 200
        assert 'Psicólogo Teste' in response.get_data(as_text=True)

    def test_agendamentos_without_filters(self, client, admin_user):
        """Testa a página de agendamentos sem filtros"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        response = client.get(url_for('admin.agendamentos'))
        assert response.status_code == 200

    def test_agendamentos_with_filters(self, client, admin_user, sample_paciente, sample_psicologo):
        """Testa a página de agendamentos com filtros aplicados"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        # Criar um agendamento para teste
        with client.application.app_context():
            agendamento = Agendamento(
                paciente_id=sample_paciente.id,
                psicologo_id=sample_psicologo.id,
                data_hora=datetime.now() + timedelta(days=1),
                status='agendado',
                observacoes='Teste'
            )
            db.session.add(agendamento)
            db.session.commit()
        
        # Testar com filtro de psicólogo
        response = client.get(url_for('admin.agendamentos', psicologo_id=sample_psicologo.id))
        assert response.status_code == 200

    def test_agendamentos_date_filters(self, client, admin_user):
        """Testa filtros de data nos agendamentos"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        response = client.get(url_for('admin.agendamentos', 
                                    data_inicio=today.strftime('%Y-%m-%d'),
                                    data_fim=tomorrow.strftime('%Y-%m-%d')))
        assert response.status_code == 200

    def test_agendamentos_status_filter(self, client, admin_user):
        """Testa filtro por status nos agendamentos"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        response = client.get(url_for('admin.agendamentos', status='agendado'))
        assert response.status_code == 200

    def test_unauthorized_access_perfil(self, client, app):
        """Testa acesso não autorizado à página de perfil"""
        with app.app_context():
            response = client.get(url_for('admin.perfil'))
            assert response.status_code == 302  # Redirect para login

    def test_unauthorized_access_listar_pacientes(self, client, app):
        """Testa acesso não autorizado à listagem de pacientes"""
        with app.app_context():
            response = client.get(url_for('admin.listar_pacientes'))
            assert response.status_code == 302  # Redirect para login

    def test_unauthorized_access_listar_psicologos(self, client, app):
        """Testa acesso não autorizado à listagem de psicólogos"""
        with app.app_context():
            response = client.get(url_for('admin.listar_psicologos'))
            assert response.status_code == 302  # Redirect para login

    def test_unauthorized_access_agendamentos(self, client, app):
        """Testa acesso não autorizado à página de agendamentos"""
        with app.app_context():
            response = client.get(url_for('admin.agendamentos'))
            assert response.status_code == 302  # Redirect para login

    def test_dashboard_buttons_present(self, client, admin_user, sample_agendamentos, app):
        """Testa se os novos botões estão presentes no dashboard"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
        
        with app.app_context():
            response = client.get(url_for('admin.dashboard'))
            assert response.status_code == 200