import os


bind = "127.0.0.1:8000"
workers = int(os.environ.get("WEB_CONCURRENCY", "3"))
worker_class = "gthread"
threads = 2

timeout = 60
graceful_timeout = 30
keepalive = 5
backlog = 2048

max_requests = 1000
max_requests_jitter = 100

forwarded_allow_ips = "127.0.0.1"
accesslog = "-"
errorlog = "-"
capture_output = True
