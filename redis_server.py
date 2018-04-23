import asyncio
from asyncio import StreamWriter, StreamReader
from typing import Optional, List

from aioredis import Redis
from async_timeout import timeout
from sanic import Blueprint, Sanic

from cache import Cache
from sanic.log import logger
from config import *

bp = Blueprint('redis_server')
logger = logger.getChild('redis_server')


@bp.listener('before_server_start')
async def attach(app: Sanic, _loop):
    app.redis_server = RedisServer(app.redis, app.cache, REDIS_SERVER_LISTEN_PORT)

    await app.redis_server.start()


@bp.listener('after_server_stop')
async def detach(app: Sanic, _loop):
    await app.redis_server.stop()


class RedisServer:
    def __init__(self, redis: Redis, cache: Cache, port: int):
        self.port = port
        self.cache = cache
        self.redis = redis
        self.server = None

    # noinspection PyBroadException
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        while not reader.at_eof():
            try:
                array = await reader.readline()

                if reader.at_eof():
                    break

                assert array[:1] == b'*'

                count = parse_int(array[1:-2])

                items = [await read_bulk_string(reader) for _ in range(count)]
                command = items[0]
                params = items[1:]

                try:
                    with timeout(REDIS_SERVER_TIMEOUT):
                        await self._execute(command, params, writer)
                except Exception:
                    logger.exception(f"Command failed: {command}")
                    writer.write(encode_error("Command failed"))
            except Exception:
                logger.exception(f"Invalid command: {array}")
                writer.write(encode_error("Invalid command"))
                writer.close()

    async def _execute(self, command: bytes, params: List[bytes], writer: StreamWriter):
        if command == b'PING':
            response = await self.redis.ping()
            writer.write(encode_string(response))

        elif command == b'GET':
            key = params[0]
            value = self.cache.get(key)

            if value is None:
                value = await self.redis.get(key)

            if value is not None:
                self.cache[key] = value

            writer.write(encode_bulk_string(value))
        else:
            writer.write(encode_error(f"Command '{command}' is not supported"))

    async def start(self):
        self.server = await asyncio.start_server(self._handle_client, '0.0.0.0', self.port)

        logger.info(f"Redis server at 0.0.0.0:{self.port}")

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()


def parse_int(data: bytes):
    return int(data.decode('ascii'))


async def read_bulk_string(reader: StreamReader) -> Optional[bytes]:
    header = await reader.readline()

    assert header[:1] == b'$'

    length = parse_int(header[1:-2])

    if length == 0:
        return b''

    if length == -1:
        return None

    value = await reader.readexactly(length + 2)

    return value[0:-2]


def encode_bulk_string(value: Optional[bytes]) -> bytes:
    if value is None:
        return b'$-1\r\n'
    else:
        return b'$' + str(len(value)).encode() + b'\r\n' + value + b'\r\n'


def encode_string(string: bytes) -> bytes:
    return b'+' + string + b'\r\n'


def encode_error(message: str) -> bytes:
    return b'-Error ' + message.encode() + b'\r\n'
