
import logging
import os
from dotenv import load_dotenv

from copilot.application import Application, Settings


logName = __name__
if logName == "__main__":
    logName = os.path.basename(__file__)
logFormat = "%(asctime)s [%(levelname)s] %(name)s %(message)s"
logLevel = logging.INFO
log = logging.getLogger(logName)

load_dotenv()



if __name__ == "__main__":
    settings = Settings(
        debug=os.getenv("DEBUG", "false").lower() == "true",
        openaiApiKey=os.getenv("OPENAI_API_KEY")
    )
    if settings.debug:
        logLevel = logging.DEBUG
    logging.basicConfig(format=logFormat, level=logLevel)
    app = Application(settings)
    log.info("Starting Flask app")
    app.run()
    log.info("Flask app stopped")
    app.deinit()