from sanic import Sanic

import api
from config import *

if __name__ == '__main__':
    app = Sanic()
    app.blueprint(api.bp)
    app.run(host='0.0.0.0', port=LISTEN_PORT, access_log=False, workers=WORKERS)
