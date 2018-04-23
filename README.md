# Redis Proxy

Caching Redis proxy with HTTP and Redis API.

Tryout HTTP API:
```bash
docker-compose up -d redis app
docker-compose exec redis redis-cli SET hello world
curl $(docker-compose port app 80)/values/hello
```

Tryout Redis API:
```bash
docker-compose up -d redis app
docker-compose exec redis redis-cli SET hello world
redis-cli -p $(docker-compose port app 6379 | cut -d : -f 2) GET hello
```

The solution is written in Python 3.6.

## Features

* Restful HTTP API
* Limited Redis API (only GET and PING)
* Asynchronous I/O
* Redis backend connection pooling
* Supports both string and binary keys
* Health check

## Configuration

The proxy is configured via environment variables:

Name                     | Description 
-------------------------|------------------------------------------------------------------
LISTEN_PORT              | Port the HTTP API listens on (default: 80).
WORKERS                  | Number of worker processes (default: 1). 
REDIS_CONNECT            | Redis connection string (e.g.: `redis://localhost:6379`).
REDIS_DB                 | Redis database index to connect (default: 0).
MAX_CONCURRENCY          | Maximum concurrent connections to the Redis backend (default: 1). 
CACHE_CAPACITY           | Cache capacity.
CACHE_TTL                | Cache global ttl.
REDIS_SERVER_LISTEN_PORT | Port the Redis API listens on (default: 6379). Set 0 to disable.
REDIS_SERVER_TIMEOUT     | Redis API command timeout (default: 1s).

## HTTP API

The proxy exposes HTTP Restful API for getting values.

It supports both string keys:

```text
GET /values/&lt;string_key&gt;
```

and binary keys as base64 encoded strings (`b=1` query parameter must be set):

```text
GET /values/&lt;base64_encoded_binary_key&gt;?b=1
```

## Cache

LRU cache with global expiration.

Read and write complexity is O(1).

## Tests

Prerequisites:
- docker 17.09.0+
- docker-compose 3.4+

Use this command to run tests:

```bash
make test
```

The command runs tests using `docker-compose`.

It takes about a minute to build everything and run all the tests.

The test suite has both integration and unit tests.

Integration tests are relying on `docker-compose` to spin up Redis instance.


## Log Work

| Part           | Time Spent  |
| -------------- |------------ |
| Infrastructure | 30m         |
| HTTP API       | 45m         |
| Redis API      | 45m         |
| Cache          | 40m         |
| Documentation  | 20m         |

Time spent includes time for design decisions and unit tests.

## TODO

- [ ] Prometheus metrics endpoint
- [ ] Structured logging in JSON format
- [ ] Cache control headers

