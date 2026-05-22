import multiprocessing

# Binding — Gunicorn listens locally only; Nginx proxies externally
bind = "127.0.0.1:8000"

# Workers: (2 x CPU cores) + 1
workers = (multiprocessing.cpu_count() * 2) + 1
worker_class = "sync"
threads = 2

# Timeouts
timeout = 120
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = "/var/www/demo_company_tickets/logs/gunicorn_access.log"
errorlog  = "/var/www/demo_company_tickets/logs/gunicorn_error.log"
loglevel  = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"'

# Process naming
proc_name = "demo_company_tickets"

# Security — drop privileges after binding
user  = "nash_tickets"
group = "nash_tickets"

limit_request_line   = 4094
limit_request_fields = 100
