from base64 import b64decode

from aioredis import create_redis_pool
from async_timeout import timeout
from sanic import Sanic
from sanic.blueprints import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, raw, text

from cache import Cache
from config import *

bp = Blueprint('api')


@bp.get('/status')
async def status(request: Request) -> HTTPResponse:
    redis = request.app.redis

    with timeout(1):
        result = await redis.ping()

    if result != b'PONG':
        return HTTPResponse("Backend is not Redis", status=500)

    return text("OK", status=200)


@bp.get('/values/<key>')
async def get_value(request: Request, key) -> HTTPResponse:
    if request.args.get('b') == '1':
        key = b64decode(key)

    cached = request.app.cache.get(key)

    if cached is not None:
        return raw(cached)

    redis = request.app.redis
    result = await redis.get(key)

    if result is None:
        return HTTPResponse(status=404)

    request.app.cache[key] = result

    return raw(result)


@bp.listener('before_server_start')
async def init(app: Sanic, _):
    with timeout(1):
        app.redis = await create_redis_pool(REDIS_CONNECT, db=REDIS_DB, maxsize=MAX_CONCURRENCY)

    app.cache = Cache(CACHE_CAPACITY, CACHE_TTL)


@bp.listener('after_server_stop')
async def shutdown(app: Sanic, _):
    app.redis.close()
    await app.redis.wait_closed()
