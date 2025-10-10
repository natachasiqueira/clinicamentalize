# Sistema Clínica Mentalize

Sistema web completo para gestão de clínica de psicologia desenvolvido em Flask com dashboard administrativo avançado e funcionalidades completas de agendamento e prontuários.

## 🚀 Funcionalidades

### Área Pública
- **Página inicial**: Informações da clínica e formulário de cadastro de pacientes
- **Sistema de login**: Autenticação segura para diferentes tipos de usuários
- **Página de contato**: Formulário de contato integrado com EmailJS para envio de emails

### Área do Paciente
- **Dashboard pessoal**: Visão geral dos agendamentos e informações
- **Gestão de perfil**: Atualização de dados pessoais e contato
- **Agendamentos**: Visualização e gestão de consultas agendadas
- **Histórico**: Acesso ao histórico de sessões realizadas

### Área do Psicólogo
- **Dashboard profissional**: Visão geral da agenda e pacientes
- **Calendário interativo**: Gestão completa de horários e agendamentos
- **Prontuários eletrônicos**: Sistema completo de registro de sessões
- **Gestão de horários**: Configuração de disponibilidade de atendimento
- **Relatórios**: Acompanhamento de pacientes e sessões

### Área Administrativa
- **Dashboard executivo**: Indicadores e métricas avançadas da clínica
  - Estatísticas gerais (total de pacientes, psicólogos e agendamentos)
  - Gráficos interativos de agendamentos por mês
  - Taxa de retenção de pacientes com análise temporal
  - Distribuição de frequência de sessões por paciente
  - Taxa de ocupação individual dos profissionais
  - Taxa de no-show mensal com tendências
  - Número de casos ativos por profissional
- **Gestão de usuários**: Sistema completo de administração de usuários
  - Cadastro de novos psicólogos com validações
  - Listagem de pacientes com filtros avançados (nome, email, telefone)
  - Listagem de psicólogos com sistema de busca e filtros
- **Gestão de agendamentos**: Controle total dos agendamentos da clínica
  - Visualização de todos os agendamentos do sistema
  - Filtros por psicólogo, paciente, status e período
  - Análise de status dos agendamentos (agendado, confirmado, realizado, cancelado, ausência)
- **Perfil administrativo**: Gestão do próprio perfil
  - Edição de dados pessoais do administrador
  - Alteração segura de senha com validações


### Sistema de Prontuários
- **Registro de sessões**: Documentação completa dos atendimentos
- **Histórico de pacientes**: Acompanhamento longitudinal
- **Recorrência de atendimentos**: Controle de frequência e continuidade

## 🛠️ Tecnologias

### Backend
- **Flask 2.3.3**: Framework web principal
- **SQLAlchemy 3.0.5**: ORM para banco de dados
- **Flask-Login 0.6.3**: Sistema de autenticação
- **Flask-WTF 1.1.1**: Formulários e validação
- **Flask-Migrate 4.0.5**: Migrações de banco de dados
- **Flask-CORS 4.0.0**: Controle de CORS
- **Werkzeug 2.3.7**: Utilitários WSGI
- **PyJWT 2.8.0**: Tokens JWT para autenticação

### Frontend
- **HTML5**: Estrutura semântica
- **CSS3**: Estilização moderna e responsiva
- **JavaScript ES6+**: Interatividade e funcionalidades dinâmicas
- **Chart.js**: Gráficos interativos no dashboard
- **Bootstrap**: Framework CSS para responsividade

### Banco de Dados
- **SQLite**: Desenvolvimento local
- **PostgreSQL**: Produção (configurável)

### Testes
- **Pytest 7.4.2**: Framework de testes
- **Pytest-Flask 1.2.0**: Extensões para Flask
- **Pytest-Cov 4.1.0**: Cobertura de código

## 📋 Pré-requisitos

- **Python 3.8+**
- **pip** (gerenciador de pacotes Python)
- **Git** (para clonagem do repositório)



**Usuário padrão criado automaticamente**:
  - **Admin**: admin@clinicamentalize.com.br (senha: admin123)
    - Acesso completo ao dashboard administrativo
    - Permissões para cadastrar psicólogos
    - Visualização de relatórios e métricas avançadas
    - Gestão de todos os usuários e agendamentos do sistema


## 🗄️ Modelos de Dados

### Usuario
- Usuários do sistema (admin, psicólogo, paciente)
- Autenticação e autorização

### Psicologo
- Dados profissionais dos psicólogos

### Paciente
- Informações dos pacientes
- Dados pessoais e histórico

### Agendamento
- Consultas agendadas
- Status e informações da sessão

### Sessao
- Registro das sessões realizadas
- Prontuários e observações

### Prontuario
- Histórico clínico dos pacientes
- Evolução e acompanhamento

### HorarioAtendimento
- Disponibilidade dos psicólogos
- Configuração de horários

## 🔒 Segurança

- **Autenticação**: Sistema seguro com hash de senhas
- **Autorização**: Controle de acesso por tipo de usuário
- **Validação**: Formulários com validação server-side
- **CSRF Protection**: Proteção contra ataques CSRF
- **SQL Injection**: Proteção via SQLAlchemy ORM

## 🌐 Deploy em Produção

### Configurações recomendadas:
- **Servidor**: Gunicorn + Nginx
- **Banco**: PostgreSQL
- **SSL**: Certificado HTTPS
- **Backup**: Rotina automatizada
- **Monitoramento**: Logs e métricas