import pytz
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Usuario, Psicologo, Paciente, Agendamento, Admin, db
from sqlalchemy import func, case, String, cast
from functools import wraps
from werkzeug.security import generate_password_hash
import os

def admin_required(f):
    """Decorator para verificar se o usuário é admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo_usuario != 'admin':
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def init_routes(admin):
    """Inicializa as rotas do admin"""
    
    @admin.route('/dashboard')
    @login_required
    @admin_required
    def dashboard():
        """Dashboard administrativo"""
        # Estatísticas básicas
        total_pacientes = db.session.query(Paciente).join(Usuario, Paciente.usuario_id == Usuario.id).count()
        total_psicologos = db.session.query(Psicologo).join(Usuario, Psicologo.usuario_id == Usuario.id).filter(Usuario.tipo_usuario == 'psicologo').count()
        total_agendamentos = db.session.query(Agendamento).count()
        
        # Dados reais para os gráficos
        from datetime import datetime, timedelta
        
        # Defina o fuso horário para UTC para evitar erros de comparação
        agora_utc = datetime.now(pytz.utc)
        data_limite = agora_utc - timedelta(days=180)  # aproximadamente 6 meses

        # Agendamentos por mês (últimos 6 meses)
        agendamentos_query = db.session.query(
            func.to_char(Agendamento.data_hora, 'MM').label('mes_num'),
            func.count(Agendamento.id).label('total')
        ).filter(
            Agendamento.data_hora >= data_limite
        ).group_by(
            func.to_char(Agendamento.data_hora, 'MM')
        ).order_by(
            func.to_char(Agendamento.data_hora, 'MM')
        ).all()
        
        # Converter números dos meses para nomes
        meses_nomes = {
            '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr',
            '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago',
            '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
        }
        
        agendamentos_por_mes = []
        for item in agendamentos_query:
            mes_nome = meses_nomes.get(item.mes_num, item.mes_num)
            agendamentos_por_mes.append({'mes': mes_nome, 'total': item.total})
        
        # 1. Taxa de Retenção de Pacientes (por mês)
        # Primeiro, obter todos os meses com agendamentos
        meses_query = db.session.query(
            func.to_char(Agendamento.data_hora, 'YYYY-MM').label('mes')
        ).filter(
            Agendamento.data_hora >= data_limite,
            Agendamento.status.in_(['realizado', 'confirmado'])
        ).group_by(
            func.to_char(Agendamento.data_hora, 'YYYY-MM')
        ).all()
        
        taxa_retencao = []
        for mes_item in meses_query:
            mes = mes_item.mes
            
            # Total de pacientes únicos no mês
            -            total_pacientes = db.session.query(
            +            total_pacientes_mes = db.session.query(
                             func.count(func.distinct(Agendamento.paciente_id))
                         ).filter(
                             func.to_char(Agendamento.data_hora, 'YYYY-MM') == mes,
                             Agendamento.status.in_(['realizado', 'confirmado'])
                         ).scalar() or 0
                         
                         # Pacientes que tiveram mais de 1 sessão no mês
                         pacientes_multiplas_sessoes = db.session.query(
                             Agendamento.paciente_id
                         ).filter(
                             func.to_char(Agendamento.data_hora, 'YYYY-MM') == mes,
                             Agendamento.status.in_(['realizado', 'confirmado'])
                         ).group_by(
                             Agendamento.paciente_id
                         ).having(
                             func.count(Agendamento.id) >= 2
                         ).count()
                         
            -            if total_pacientes > 0:
            -                taxa = (pacientes_multiplas_sessoes / total_pacientes) * 100
            +            if total_pacientes_mes > 0:
            +                taxa = (pacientes_multiplas_sessoes / total_pacientes_mes) * 100
                             taxa_retencao.append({
                                 'mes': mes,
                                 'taxa': round(taxa, 1)
                             })
                         else:
                             taxa_retencao.append({
                                 'mes': mes,
                                 'taxa': 0
                             })
        
        # 2. Frequência de Sessões (distribuição)
        frequencia_query = db.session.query(
            Agendamento.paciente_id,
            func.count(Agendamento.id).label('total_sessoes')
        ).filter(
            Agendamento.status == 'realizado'
        ).group_by(Agendamento.paciente_id).all()
        
        distribuicao_sessoes = {'1-5': 0, '6-10': 0, '11-15': 0, '16+': 0}
        for item in frequencia_query:
            if item.total_sessoes <= 5:
                distribuicao_sessoes['1-5'] += 1
            elif item.total_sessoes <= 10:
                distribuicao_sessoes['6-10'] += 1
            elif item.total_sessoes <= 15:
                distribuicao_sessoes['11-15'] += 1
            else:
                distribuicao_sessoes['16+'] += 1
        
        # 3. Taxa de Ocupação dos Profissionais
        ocupacao_query = db.session.query(
            Usuario.nome_completo.label('nome'),
            func.count(Agendamento.id).label('agendamentos_realizados')
        ).join(
            Psicologo, Usuario.id == Psicologo.usuario_id
        ).outerjoin(
            Agendamento, Psicologo.id == Agendamento.psicologo_id
        ).filter(
            Usuario.tipo_usuario == 'psicologo',
            Agendamento.data_hora >= data_limite
        ).group_by(
            Usuario.nome_completo
        ).all()
        
        # Assumindo 40 horas/semana * 4 semanas * 6 meses = 960 horas disponíveis
        horas_disponiveis = 960
        taxa_ocupacao = []
        for item in ocupacao_query:
            # Assumindo 1 hora por sessão
            ocupacao = (item.agendamentos_realizados / horas_disponiveis) * 100
            taxa_ocupacao.append({
                'nome': item.nome.split()[0],  # Primeiro nome
                'ocupacao': round(ocupacao, 1)
            })
        
        # 4. Taxa de No-Show (por mês)
        noshow_query = db.session.query(
            func.to_char(Agendamento.data_hora, 'YYYY-MM').label('mes'),
            func.count(Agendamento.id).label('total_agendamentos'),
            func.sum(case((Agendamento.status == 'ausencia', 1), else_=0)).label('faltas')
        ).filter(
            Agendamento.data_hora >= data_limite
        ).group_by(
            func.to_char(Agendamento.data_hora, 'YYYY-MM')
        ).all()
        
        taxa_noshow = []
        for item in noshow_query:
            if item.total_agendamentos > 0:
                taxa = (item.faltas / item.total_agendamentos) * 100
                mes_formatado = item.mes.split('-')[1] + '/' + item.mes.split('-')[0][-2:]
                taxa_noshow.append({'mes': mes_formatado, 'taxa': round(taxa, 1)})
        
        # 5. Número de Casos Ativos por Profissional
        casos_ativos_query = db.session.query(
            Usuario.nome_completo.label('nome'),
            func.count(func.distinct(Agendamento.paciente_id)).label('casos_ativos')
        ).join(
            Psicologo, Usuario.id == Psicologo.usuario_id
        ).outerjoin(
            Agendamento, Psicologo.id == Agendamento.psicologo_id
        ).filter(
            Usuario.tipo_usuario == 'psicologo',
            Agendamento.status.in_(['agendado', 'confirmado', 'realizado']),
            Agendamento.data_hora >= agora_utc - timedelta(days=90)  # últimos 3 meses
        ).group_by(
            Usuario.nome_completo
        ).all()
        
        casos_ativos = []
        for item in casos_ativos_query:
            casos_ativos.append({
                'nome': item.nome.split()[0],  # Primeiro nome
                'casos': item.casos_ativos
            })
        
        return render_template('admin/dashboard.html', 
                             total_pacientes=total_pacientes,
                             total_psicologos=total_psicologos,
                             total_agendamentos=total_agendamentos,
                             agendamentos_por_mes=agendamentos_por_mes,
                             taxa_retencao=taxa_retencao,
                             distribuicao_sessoes=distribuicao_sessoes,
                             taxa_ocupacao=taxa_ocupacao,
                             taxa_noshow=taxa_noshow,
                             casos_ativos=casos_ativos)
    
    @admin.route('/cadastrar_psicologo', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def cadastrar_psicologo():
        """Cadastrar novo psicólogo"""
        if request.method == 'POST':
            nome_completo = request.form.get('nome_completo')
            email = request.form.get('email')
            telefone = request.form.get('telefone')
            senha = request.form.get('senha')
            confirmar_senha = request.form.get('confirmar_senha')
            
            # Validações básicas
            if not all([nome_completo, email, telefone, senha, confirmar_senha]):
                flash('Todos os campos são obrigatórios!', 'error')
                return render_template('admin/cadastrar_psicologo.html')
            
            if senha != confirmar_senha:
                flash('As senhas não coincidem!', 'error')
                return render_template('admin/cadastrar_psicologo.html')
            
            if len(senha) < 6:
                flash('A senha deve ter pelo menos 6 caracteres!', 'error')
                return render_template('admin/cadastrar_psicologo.html')
            
            try:
                # Verificar se o email já existe
                usuario_existente = Usuario.query.filter_by(email=email).first()
                if usuario_existente:
                    flash('Este email já está cadastrado!', 'error')
                    return render_template('admin/cadastrar_psicologo.html')
                
                # Criar novo usuário
                novo_usuario = Usuario(
                    nome_completo=nome_completo,
                    email=email,
                    telefone=telefone,
                    tipo_usuario='psicologo'
                )
                novo_usuario.set_senha(senha)
                
                db.session.add(novo_usuario)
                db.session.flush()  # Para obter o ID do usuário
                
                # Criar registro de psicólogo
                novo_psicologo = Psicologo(usuario_id=novo_usuario.id)
                db.session.add(novo_psicologo)
                
                db.session.commit()
                
                flash('Psicólogo cadastrado com sucesso!', 'success')
                return redirect(url_for('admin.dashboard'))
                
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao cadastrar psicólogo: {e}")
                return render_template('admin/cadastrar_psicologo.html')
        
        return render_template('admin/cadastrar_psicologo.html')
    
    @admin.route('/perfil', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def perfil():
        """Editar perfil do administrador"""
        admin_user = current_user
        
        if request.method == 'POST':
            try:
                # Atualizar dados básicos
                admin_user.nome_completo = request.form.get('nome_completo')
                admin_user.email = request.form.get('email')
                admin_user.telefone = request.form.get('telefone')
                
                # Verificar se foi solicitada mudança de senha
                nova_senha = request.form.get('nova_senha')
                confirmar_senha = request.form.get('confirmar_senha')
                
                if nova_senha:
                    if nova_senha != confirmar_senha:
                        flash('As senhas não coincidem.', 'error')
                        return render_template('admin/perfil.html', admin=admin_user)
                    
                    if len(nova_senha) < 6:
                        flash('A senha deve ter pelo menos 6 caracteres.', 'error')
                        return render_template('admin/perfil.html', admin=admin_user)
                    
                    admin_user.senha_hash = generate_password_hash(nova_senha)
                
                db.session.commit()
                flash('Perfil atualizado com sucesso!', 'success')
                return redirect(url_for('admin.dashboard'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao atualizar perfil: {str(e)}', 'error')
        
        return render_template('admin/perfil.html', admin=admin_user)
    
    @admin.route('/listar-pacientes')
    @login_required
    @admin_required
    def listar_pacientes():
        """Listar todos os pacientes do sistema com filtros"""
        # Parâmetros de filtro
        nome_filtro = request.args.get('nome', '').strip()
        email_filtro = request.args.get('email', '').strip()
        telefone_filtro = request.args.get('telefone', '').strip()
        
        # Query base
        query = db.session.query(Paciente, Usuario).join(
            Usuario, Paciente.usuario_id == Usuario.id
        )
        
        # Aplicar filtros
        if nome_filtro:
            query = query.filter(Usuario.nome_completo.ilike(f"%{nome_filtro}%"))
        
        if email_filtro:
            query = query.filter(Usuario.email.ilike(f"%{email_filtro}%"))
            
        if telefone_filtro:
            query = query.filter(Usuario.telefone.ilike(f"%{telefone_filtro}%"))
        
        pacientes = query.order_by(Usuario.nome_completo).all()
        
        # Criar objeto de filtros para o template
        filtros = {
            'nome': nome_filtro,
            'email': email_filtro,
            'telefone': telefone_filtro
        }

        return render_template('admin/listar_pacientes.html', 
                             pacientes=pacientes,
                             filtros=filtros)
    
    @admin.route('/listar-psicologos')
    @login_required
    @admin_required
    def listar_psicologos():
        """Listar todos os psicólogos do sistema com filtros"""
        # Parâmetros de filtro
        nome_filtro = request.args.get('nome', '').strip()
        email_filtro = request.args.get('email', '').strip()
        telefone_filtro = request.args.get('telefone', '').strip()
        
        # Query base
        query = db.session.query(Psicologo, Usuario).join(
            Usuario, Psicologo.usuario_id == Usuario.id
        )
        
        # Aplicar filtros
        if nome_filtro:
            query = query.filter(Usuario.nome_completo.ilike(f"%{nome_filtro}%"))
        
        if email_filtro:
            query = query.filter(Usuario.email.ilike(f"%{email_filtro}%"))
            
        if telefone_filtro:
            query = query.filter(Usuario.telefone.ilike(f"%{telefone_filtro}%"))
        
        psicologos = query.order_by(Usuario.nome_completo).all()
        
        # Criar objeto de filtros para o template
        filtros = {
            'nome': nome_filtro,
            'email': email_filtro,
            'telefone': telefone_filtro
        }
        
        return render_template('admin/listar_psicologos.html', 
                             psicologos=psicologos,
                             filtros=filtros)
    
    @admin.route('/agendamentos')
    @login_required
    @admin_required
    def agendamentos():
        """Listar todos os agendamentos com filtros"""
        # Parâmetros de filtro
        psicologo_nome_filtro = request.args.get('psicologo_nome', '').strip()
        paciente_nome_filtro = request.args.get('paciente_nome', '').strip()
        status_filtro = request.args.get('status')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Criar aliases para evitar conflitos
        from sqlalchemy.orm import aliased
        UsuarioPaciente = aliased(Usuario)
        UsuarioPsicologo = aliased(Usuario)
        
        # Query base
        query = db.session.query(
            Agendamento,
            UsuarioPaciente.nome_completo.label('paciente_nome'),
            UsuarioPsicologo.nome_completo.label('psicologo_nome')
        ).join(
            Paciente, Agendamento.paciente_id == Paciente.id
        ).join(
            UsuarioPaciente, Paciente.usuario_id == UsuarioPaciente.id
        ).join(
            Psicologo, Agendamento.psicologo_id == Psicologo.id
        ).join(
            UsuarioPsicologo, Psicologo.usuario_id == UsuarioPsicologo.id
        )
        
        # Aplicar filtros
        if psicologo_nome_filtro:
            query = query.filter(UsuarioPsicologo.nome_completo.ilike(f"%{psicologo_nome_filtro}%"))
        
        if paciente_nome_filtro:
            query = query.filter(UsuarioPaciente.nome_completo.ilike(f"%{paciente_nome_filtro}%"))
        
        if status_filtro:
            query = query.filter(Agendamento.status == status_filtro)
        
        if data_inicio:
            from datetime import datetime
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(func.date(Agendamento.data_hora) >= data_inicio_dt.date())
        
        if data_fim:
            from datetime import datetime
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(func.date(Agendamento.data_hora) <= data_fim_dt.date())
        
        agendamentos = query.order_by(Agendamento.data_hora.desc()).all()
        
        status_opcoes = ['agendado', 'confirmado', 'realizado', 'cancelado', 'ausencia']
        
        return render_template('admin/agendamentos.html', 
                             agendamentos=agendamentos,
                             status_opcoes=status_opcoes,
                             filtros={
                                 'psicologo_nome': psicologo_nome_filtro,
                                 'paciente_nome': paciente_nome_filtro,
                                 'status': status_filtro,
                                 'data_inicio': data_inicio,
                                 'data_fim': data_fim
                              })
    
    @admin.route('/db-info')
    @login_required
    @admin_required
    def db_info():
        """Informações de diagnóstico do banco de dados (mascara credenciais)"""
        from flask import current_app
        import os
    
        # Obter URI configurada na aplicação e mascarar credenciais
        uri = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        masked_uri = None
        if uri:
            try:
                if '://' in uri and '@' in uri:
                    scheme, rest = uri.split('://', 1)
                    creds, hostpart = rest.split('@', 1)
                    masked_uri = f"{scheme}://***:***@{hostpart}"
                else:
                    masked_uri = uri
            except Exception:
                masked_uri = 'unavailable'
    
        # Checar variável de ambiente DATABASE_URL e mascarar
        env_has_dburl = 'DATABASE_URL' in os.environ
        env_db = os.environ.get('DATABASE_URL')
        masked_env_db = None
        if env_db:
            try:
                if '://' in env_db and '@' in env_db:
                    scheme, rest = env_db.split('://', 1)
                    creds, hostpart = rest.split('@', 1)
                    masked_env_db = f"{scheme}://***:***@{hostpart}"
                else:
                    masked_env_db = env_db
            except Exception:
                masked_env_db = 'unavailable'
    
        # Contagens básicas
        usuarios_total = db.session.query(Usuario).count()
        usuarios_pacientes = db.session.query(Usuario).filter(Usuario.tipo_usuario == 'paciente').count()
        pacientes_total = db.session.query(Paciente).count()
        pacientes_join_usuario = db.session.query(Paciente).join(Usuario, Paciente.usuario_id == Usuario.id).count()
    
        # Amostra de pacientes (id, nome, email)
        amostra = db.session.query(Paciente).join(Usuario, Paciente.usuario_id == Usuario.id)\
            .with_entities(Paciente.id, Usuario.nome_completo, Usuario.email).limit(10).all()
    
        return jsonify({
            'app_SQLALCHEMY_DATABASE_URI': masked_uri,
            'env_DATABASE_URL_present': env_has_dburl,
            'env_DATABASE_URL': masked_env_db,
            'usuarios_total': usuarios_total,
            'usuarios_pacientes': usuarios_pacientes,
            'pacientes_total': pacientes_total,
            'pacientes_join_usuario': pacientes_join_usuario,
            'pacientes_amostra': [
                {'id': p[0], 'nome': p[1], 'email': p[2]} for p in amostra
            ]
        })