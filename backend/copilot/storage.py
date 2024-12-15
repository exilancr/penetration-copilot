

import os
import json
from pydantic import BaseModel
import uuid


import sqlalchemy as SQA
from copilot.models import AlchemyModel





class Storage:
    def __init__(self, settings):
        self.dataPath = os.path.join(settings.dataDir, 'penetration-copilot')
        if not os.path.exists(self.dataPath):
            os.makedirs(self.dataPath)
        self.postingsPath = os.path.join(self.dataPath, "postings")
        if not os.path.exists(self.postingsPath):
            os.makedirs(self.postingsPath)
        self.profilesPath = os.path.join(self.dataPath, "profiles")
        if not os.path.exists(self.profilesPath):
            os.makedirs(self.profilesPath)
        self.dbFilePath = os.path.join(self.dataPath, "db.sqlite")
        self.dbUrl = f"sqlite:///{self.dbFilePath}"
        self.dbEngine = SQA.create_engine(self.dbUrl)
        if not os.path.exists(self.dbFilePath):
            AlchemyModel.metadata.create_all(self.dbEngine)
        self.dbSession = SQA.orm.sessionmaker(bind=self.dbEngine)()
        self.kvdb = {}
