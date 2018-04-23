from sanic import Sanic

import api
import redis_server
from config import *

if __name__ == '__main__':
    app = Sanic()
    app.blueprint(api.bp)

    if REDIS_SERVER_LISTEN_PORT:
        app.blueprint(redis_server.bp)

    app.run(host='0.0.0.0', port=LISTEN_PORT, access_log=False, workers=WORKERS)
