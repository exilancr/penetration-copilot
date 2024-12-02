

from flask import Flask, current_app
from pydantic import BaseModel

from copilot.controllers import ControllerBase
from copilot.storage import Storage
from copilot.views import register_views
from copilot.formatters import register_formatters
from copilot.intelligence import register_intelligence
from copilot.tasks import TaskProcessor
from copilot.scraping import register_scraping

import os


class Settings(BaseModel):
    debug: bool = False
    openaiApiKey: str = None

class Application(Flask):
    _instance = None
    def __init__(self, settings: Settings):
        super().__init__(__name__)
        self.settings = settings
        self.debug = settings.debug
        self.intelligence = None
        self.storage = Storage()
        self.tasks = TaskProcessor(os.cpu_count())
        ControllerBase.register(self)
        register_views(self)
        register_formatters(self)
        register_intelligence(self)
        register_scraping(self)
        Application._instance = self

    @staticmethod
    def instance():
        return Application._instance

    def deinit(self):
        self.tasks.stop()
