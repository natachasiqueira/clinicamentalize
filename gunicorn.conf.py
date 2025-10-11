# Configuração do Gunicorn para Render Free Tier
import os

# Configurações básicas
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"
workers = 1  # Render Free tem limitação de memória
worker_class = "sync"
worker_connections = 1000

# Configurações de timeout - CRÍTICO para resolver WORKER TIMEOUT
timeout = 120  # Aumenta de 30s para 120s
keepalive = 5
max_requests = 1000
max_requests_jitter = 100

# Configurações de memória para Render Free
preload_app = True  # Carrega app antes de fazer fork dos workers
worker_tmp_dir = "/dev/shm"  # Usa RAM para arquivos temporários

# Logs
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de processo
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Configurações de graceful restart
graceful_timeout = 30