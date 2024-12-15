

from flask import Flask
from pydantic import BaseModel
from openai import OpenAI
import os
import requests
from authlib.jose import jwt

import logging
log = logging.getLogger(__name__)

from copilot.controllers import ControllerBase
from copilot.storage import Storage
from copilot.views import register_views
from copilot.formatters import register_formatters
from copilot.tasks import TaskProcessor
from copilot.scraping import register_scraping


class Settings(BaseModel):
    debug: bool = False
    openaiApiKey: str = None
    dataDir: str = None
    auth0Domain: str = None
    auth0Secret: str = None
    auth0ClientId: str = None
    auth0ClientSecret: str = None
    auth0Audience: str = None

    def get(self, key, default = None):
        return getattr(self, key, default)

class Auth0():
    def __init__(self, settings: Settings):
        self.jwks = self.__obtainJWKS(settings.auth0Domain)
        self.clientSecret = settings.auth0ClientSecret
        self.secret = settings.auth0Secret
        self.audience = settings.auth0Audience


    def __obtainJWKS(self, domain: str):
        log.debug(f"Obtaining JWKS from Auth0 domain: {domain}")
        jwksUrl = f"https://{domain}/.well-known/jwks.json"
        response = requests.get(jwksUrl)
        response.raise_for_status()
        jsonData = response.json()
        if "keys" not in jsonData:
            raise Exception("Invalid JWKS response from Auth0")
        return { key['kid']: key for key in jsonData["keys"] }

    def getSigningKey(self, token: str):
        from jose import jwt as jose_jwt
        header = jose_jwt.get_unverified_header(token)
        if "kid" not in header:
            raise Exception("Invalid token: 'kid' not found in header")
        kid = header["kid"]
        if kid not in self.jwks:
            raise Exception(f"Public key not found for 'kid' {kid}")
        return self.jwks[kid]

    def verifyToken(self, token: str):
        # Get the signing key from Auth0's JWKS
        signing_key = self.getSigningKey(token)
        # Decode and validate the JWT (this will check the signature, expiration, etc.)
        decoded_token = jwt.decode(token, signing_key)
        decoded_token.validate()  # This checks for expiration and other claims like audience, issuer
        if self.audience not in decoded_token.get("aud"):
            raise Exception(f"Invalid audience in token: {decoded_token.get('aud')}")
        # Return decoded token if valid
        return decoded_token


class Application():
    _instance = None
    def __init__(self, settings: Settings):
        self.flask = Flask(__name__)
        self.settings = settings
        self.flask.debug = self.settings.debug
        self.__initLogging()

        self.intelligence = OpenAI(api_key=self.settings.openaiApiKey)
        self.storage = Storage(settings)
        self.tasks = TaskProcessor(os.cpu_count())

        self.auth0 = Auth0(settings)
        ControllerBase.register(self.flask)
        register_views(self.flask)
        register_formatters(self.flask)
        register_scraping(self)


    @property
    def config(self):
        return self.settings

    def __initLogging(self):
        logFormat = "%(asctime)s [%(levelname)s] %(name)s %(message)s"
        logLevel = logging.INFO
        if self.settings.debug:
            logLevel = logging.DEBUG
        logging.basicConfig(format=logFormat, level=logLevel)


    @staticmethod
    def instance():
        if not Application._instance:
            settings = Settings(
                debug=(os.getenv("DEBUG", "false").lower() == "true"),
                openaiApiKey=os.getenv("OPENAI_API_KEY"),
                dataDir=os.getenv("DATA_DIR", "./data"),
                auth0Domain=os.getenv("AUTH0_DOMAIN"),
                auth0Secret=os.getenv("AUTH0_SECRET"),
                auth0ClientId=os.getenv("AUTH0_CLIENT_ID"),
                auth0ClientSecret=os.getenv("AUTH0_CLIENT_SECRET"),
                auth0Audience=os.getenv("AUTH0_AUDIENCE")
            )
            log.debug(f"Creating Application. Settings:\n{settings}")
            Application._instance = Application(settings)
        return Application._instance


    def deinit(self):
        self.tasks.stop()


def flask():
    return Application.instance().flask
