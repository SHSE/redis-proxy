import os
from pytimeparse import parse

LISTEN_PORT = int(os.getenv('LISTEN_PORT', 8080))
WORKERS = int(os.getenv('WORKERS', 1))
REDIS_CONNECT = os.environ['REDIS_CONNECT']
REDIS_DB = int(os.getenv('REDIS_DB', 0))
MAX_CONCURRENCY = int(os.getenv('MAX_CONCURRENCY', 1))
CACHE_CAPACITY = int(os.environ['CACHE_CAPACITY'])
CACHE_TTL = parse(os.environ['CACHE_TTL'])

assert CACHE_CAPACITY >= 1, "Cache capacity should be at least 1."
