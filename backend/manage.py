import logging
import os
from dotenv import load_dotenv

from copilot.application import Application


logName = __name__
if logName == "__main__":
    logName = os.path.basename(__file__)
log = logging.getLogger(logName)

load_dotenv()


if __name__ == "__main__":


    app = Application.instance()
    log.info("Starting Flask app")

    # TODO
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=5000)

    app.flask.run(host="0.0.0.0")
    log.info("Flask app stopped")
    app.deinit()
