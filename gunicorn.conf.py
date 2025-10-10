import os

# Configuração do Gunicorn para Render
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 1
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
worker_class = "sync"

# Logs
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Configurações de processo
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

print(f"🚀 Gunicorn configurado para: {bind}")