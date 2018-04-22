import struct
from base64 import b64encode
from datetime import datetime, timedelta

import pytest
from aioredis import create_redis
from freezegun import freeze_time
from sanic import Sanic

import api
from config import *


@pytest.yield_fixture(name='app')
def app_fixture():
    test_app = Sanic()
    test_app.blueprint(api.bp)
    yield test_app


@pytest.yield_fixture(name='redis')
def redis_fixture(loop):
    redis = loop.run_until_complete(create_redis(REDIS_CONNECT))
    yield redis
    loop.run_until_complete(redis.flushall())
    redis.close()
    loop.run_until_complete(redis.wait_closed())


@pytest.fixture(name='client')
def client_fixture(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


async def test_status_returns_200_when_healthy(client):
    response = await client.get('/status')
    assert response.status == 200


async def test_returns_string_value(redis, client):
    await redis.set('hello', b'world')

    response = await client.get('/values/hello')

    assert b'world' == await response.read()


async def test_returns_value_for_bytes_key(redis, client):
    key = struct.pack('i', 123)
    await redis.set(key, b'world')

    key = b64encode(key).decode()
    response = await client.get(f'/values/{key}?b=1')

    assert 200 == response.status
    assert b'world' == await response.read()


async def test_caches_value(redis, client):
    await redis.set('hello', b'world')
    await client.get('/values/hello')
    await redis.set('hello', b'mars')

    response = await client.get('/values/hello')

    assert b'world' == await response.read()


async def test_evicts_least_used_keys_when_cache_is_full(redis, client):
    for i in range(CACHE_CAPACITY + 1):
        await redis.set(str(i), b'cat')
        await client.get(f'/values/{i}')

    await redis.set('0', b'dog')

    response = await client.get('/values/0')

    assert b'dog' == await response.read()


async def test_misses_value_if_expired(redis, client):
    now = datetime.utcnow()

    with freeze_time(now):
        await redis.set('pet', b'cat')
        await client.get('/values/pet')
        await redis.set('pet', b'dog')

    with freeze_time(now + timedelta(seconds=CACHE_TTL + 1)):
        response = await client.get('/values/pet')

    assert b'dog' == await response.read()
