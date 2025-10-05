import pytest
from datetime import datetime, timedelta
from flask import json
from app import create_app, db
from app.models import User, Psicologo, Paciente, Horario
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False

class TestHorariosFiltragem:
    def setup_method(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Criar usuários de teste
        self.criar_usuarios_teste()
        
    def teardown_method(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def criar_usuarios_teste(self):
        # Criar psicologo
        user_psi = User(username='psi_test', email='psi@test.com', tipo='psicologo')
        user_psi.set_password('senha123')
        db.session.add(user_psi)
        db.session.commit()
        
        psicologo = Psicologo(user_id=user_psi.id, nome='Psicologo Teste', 
                             crp='12345', telefone='123456789')
        db.session.add(psicologo)
        
        # Criar paciente
        user_pac = User(username='pac_test', email='pac@test.com', tipo='paciente')
        user_pac.set_password('senha123')
        db.session.add(user_pac)
        db.session.commit()
        
        paciente = Paciente(user_id=user_pac.id, nome='Paciente Teste', 
                           cpf='12345678901', telefone='987654321')
        db.session.add(paciente)
        db.session.commit()
        
        # Login como paciente
        self.client.post('/login', data={
            'email': 'pac@test.com',
            'password': 'senha123'
        }, follow_redirects=True)
        
    def test_filtragem_horarios_futuros(self):
        """Testa se apenas horários futuros (pelo menos 1 hora à frente) são retornados"""
        # Configurar data de hoje
        hoje = datetime.now().date()
        data_str = hoje.strftime('%Y-%m-%d')
        
        # Fazer requisição para API de horários
        response = self.client.get(f'/api/horarios-disponiveis?psicologo_id=1&data={data_str}')
        assert response.status_code == 200
        
        # Verificar se todos os horários retornados estão pelo menos 1 hora à frente
        data = json.loads(response.data)
        horarios = data.get('horarios', [])
        
        hora_limite = datetime.now() + timedelta(hours=1)
        
        for horario in horarios:
            horario_datetime = datetime.strptime(f"{data_str} {horario}", '%Y-%m-%d %H:%M')
            assert horario_datetime >= hora_limite, f"Horário {horario} está menos de 1 hora à frente"