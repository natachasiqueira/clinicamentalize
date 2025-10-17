from app import create_app
from app.models import db, Paciente, Usuario
app = create_app()
from flask import current_app
with app.app_context():
    import os
    print("ENV DATABASE_URL present:", 'DATABASE_URL' in os.environ)
    print("ENV DATABASE_URL:", os.environ.get('DATABASE_URL'))
    print("Flask ENV:", current_app.config.get('ENV'))
    print("Debug:", current_app.config.get('DEBUG'))
    print("App SQLALCHEMY_DATABASE_URI:", current_app.config.get('SQLALCHEMY_DATABASE_URI'))
    print("Pacientes total:", db.session.query(Paciente).count())
    print("Pacientes join usuario:", db.session.query(Paciente).join(Usuario, Paciente.usuario_id == Usuario.id).count())
    rows = db.session.query(Paciente).join(Usuario, Paciente.usuario_id == Usuario.id).with_entities(Paciente.id, Usuario.nome_completo, Usuario.email).limit(10).all()
    for r in rows:
        print("Paciente", r[0], r[1], r[2])
