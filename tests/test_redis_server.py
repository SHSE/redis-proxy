from asyncio import AbstractEventLoop

import pytest
from pytest import raises

from cache import Cache
from redis_server import RedisServer
from aioredis import create_redis_pool, Redis, ReplyError
from config import *


@pytest.yield_fixture(name='redis_backend')
def redis_backend_fixture(loop: AbstractEventLoop):
    redis = loop.run_until_complete(create_redis_pool(REDIS_CONNECT))
    yield redis
    loop.run_until_complete(redis.flushall())
    redis.close()
    loop.run_until_complete(redis.wait_closed())


@pytest.fixture(name='cache')
def cache_fixture():
    return Cache(100, 3600)


@pytest.yield_fixture(name='redis_server')
def redis_server_fixture(loop: AbstractEventLoop, redis_backend: Redis, cache: Cache, unused_port: int):
    redis_server = RedisServer(redis_backend, cache, unused_port)
    loop.run_until_complete(redis_server.start())
    yield redis_server
    loop.run_until_complete(redis_server.stop())


@pytest.yield_fixture(name='redis_client')
def redis_client_fixture(loop: AbstractEventLoop, redis_server: RedisServer):
    redis = loop.run_until_complete(create_redis_pool(f'redis://localhost:{redis_server.port}', timeout=1))
    yield redis
    redis.close()
    loop.run_until_complete(redis.wait_closed())


async def test_ping(redis_client: Redis):
    assert b'PONG' == await redis_client.ping()


async def test_recovers_on_invalid_command(redis_client: Redis):
    with raises(ReplyError):
        await redis_client.execute(b'MEOW')

    assert b'PONG' == await redis_client.ping()


async def test_returns_value(redis_backend: Redis, redis_client: Redis):
    await redis_backend.set(b'hello', b'world')
    assert b'world' == await redis_client.get(b'hello')


async def test_caches_value(redis_backend: Redis, redis_client: Redis, cache: Cache):
    await redis_backend.set(b'hello', b'world')
    await redis_client.get(b'hello')

    assert b'world' == cache.get(b'hello')

    await redis_backend.set(b'hello', b'mars')

    assert b'world' == await redis_client.get(b'hello')


async def test_returns_none_if_value_does_not_exist(redis_client: Redis):
    assert None is await redis_client.get(b'hello')


async def test_returns_value_multiple_times(redis_backend: Redis, redis_client: Redis):
    await redis_backend.set(b'hello', b'world')

    values = [
        await redis_client.get(b'hello'),
        await redis_client.get(b'hello'),
        await redis_client.get(b'hello')
    ]

    assert [b'world'] * 3 == values
