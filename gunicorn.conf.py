import multiprocessing

# Binding — overridden by Procfile on Render ($PORT)
bind = "0.0.0.0:8000"

# Workers
workers = 2
worker_class = "sync"
threads = 2

# Timeouts
timeout = 120
keepalive = 5
graceful_timeout = 30

# Logging — stdout/stderr (works on Render and any cloud host)
accesslog = "-"
errorlog  = "-"
loglevel  = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"'

# Process naming
proc_name = "it_ticketing_system"

limit_request_line   = 4094
limit_request_fields = 100
