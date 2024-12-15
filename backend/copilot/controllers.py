
import logging

log = logging.getLogger(__name__)

from flask import Flask, request, current_app, jsonify
from six.moves.urllib.request import urlopen
from pydantic import BaseModel as PydanticModel
import json
from jose import jwt

from copilot.views import render_page

import re
import copilot.scraping as scraping
import copilot.models as models
import uuid

import os




class ControllerBase:
    __request_handlers: dict = {}

    def __init__(self):
        pass

    @staticmethod
    def register(app: Flask):
        log.debug("Registering Controllers")
        # Call derived controllers register methods
        for controller in ControllerBase.__subclasses__():
            log.debug(f"Registering controller {controller.__name__} ...")
            full_class_name = f"{controller.__module__}.{controller.__name__}"
            if full_class_name not in ControllerBase.__request_handlers:
                continue
            for method_name, method_data in ControllerBase.__request_handlers[full_class_name].items():
                log.debug(f"Registering method {method_name} ...")
                handler_lambda = lambda controller=controller, method_name=method_name, *args, **kwargs: getattr(controller(), method_name)(*args, **kwargs)
                handler_lambda.__name__ = f"{full_class_name}_{method_name}"
                app.route(controller.__prefix__ + method_data["route"], methods=method_data["methods"])(handler_lambda)

    @staticmethod
    def request(route, methods=["GET"]):
        def decorator(func):
            full_class_name = f"{func.__module__}.{'.'.join(func.__qualname__.split('.')[:-1])}"
            if full_class_name not in ControllerBase.__request_handlers:
                ControllerBase.__request_handlers[full_class_name] = {}
            ControllerBase.__request_handlers[full_class_name][func.__name__] = {
                "route": route,
                "methods": methods
            }
            return func
        return decorator

    @staticmethod
    def authenticated(permissions: list[str] = []):
        def decorator(func):
            def wrapper(*args, **kwargs):
                from  copilot.application import Application
                app = Application.instance()
                # Check if the user is authenticated
                if "Authorization" not in request.headers:
                    raise Exception("Authorization header is missing")
                token = request.headers["Authorization"].split(" ")[1]
                try:
                    verified = app.auth0.verifyToken(token)
                    log.debug(f"Authenticated user: {verified}, permissions: {permissions}")
                    for perm in permissions:
                        if perm not in verified["permissions"]:
                            raise Exception(f"Permission '{perm}' is missing")
                        log.debug(f"Permission '{perm}' is granted to user {verified['sub']}")
                        kwargs["user"] = verified
                except Exception as e:
                    raise Exception("Authentication failed")
                return func(*args, **kwargs)
            return wrapper
        return decorator





class Auth0User(PydanticModel):
    nickname: str
    name: str
    picture: str
    email: str
    email_verified: bool
    sub: str
    org_id: str|None
    updated_at: str|None
    iss: str|None
    aud: str|None
    iat: int|None
    exp: int|None
    nonce: str|None
    sid: str|None
class Auth0TokenSet(PydanticModel):
    accessToken: str
    refreshToken: str
    expiresAt: int
class Auth0Internal(PydanticModel):
    sid: str
    createdAt: int
class Auth0UserData(PydanticModel):
    user: Auth0User
    tokenSet: Auth0TokenSet
    internal: Auth0Internal|None



class AuthController(ControllerBase):
    __prefix__ = "/trueapi/auth"

    @ControllerBase.request("/store-auth0-session", methods=["PUT"])
    def storeAuth0Session(self):
        from  copilot.application import Application
        app = Application.instance()
        jsonData = request.get_json()
        userData = Auth0UserData(
            user=Auth0User.model_construct(**jsonData['user']),
            tokenSet=Auth0TokenSet.model_construct(**jsonData['tokenSet']),
            internal=Auth0Internal.model_construct(**jsonData['internal'])
        )
        log.debug(f"{self.__class__.__name__}.storeAuth0Session, user: {userData.user.sub}")

        validated_token = app.auth0.verifyToken(userData.tokenSet.accessToken)
        log.debug(f"AuthController.storeAuth0Session(), validated token.")
        userId = validated_token["sub"]

        user = app.storage.dbSession.query(models.User).filter(models.User.id == userId).one_or_none()
        if not user:
            user = models.User(id=userData.user.sub, email=userData.user.email, name=userData.user.name)
            app.storage.dbSession.add(user)
            app.storage.dbSession.commit()
            log.debug(f"AuthController.storeAuth0Session(), user created: {user}")

        log.debug(f"AuthController.storeAuth0Session(), user: {user.id}")
        return {"status": "ok"}

class TestController(ControllerBase):
    __prefix__ = "/trueapi/test"


    @ControllerBase.authenticated(permissions=['user'])
    @ControllerBase.request("/")
    def index(self, user):
        log.debug(f"{self.__class__.__name__}.index(), user: {user}")
        return {"status": "ok"}

class PostingController(ControllerBase):
    __prefix__ = "/trueapi/posting"


    @ControllerBase.authenticated(permissions=['user'])
    @ControllerBase.request("/")
    def index(self):
        app = current_app.instance()
        offset = request.args.get("offset", 0, type=int)
        count = request.args.get("count", 20, type=int)

        query = app.storage.dbSession.query(models.Posting) \
            .filter(models.Posting.duplicate==False) \
            .order_by(models.Posting.posted_at.desc())
        totalCount = query.count()
        postings =  query.limit(count).offset(offset).all()
        log.debug("PostingController.intex(), request: %s", request)
        postings = [models.PostingRepresenter.fromAlchemy(posting) for posting in postings]
        # if json requested, return json
        if request.content_type == "application/json":
            return jsonify(postings)

        # render view
        return render_page("postings.html.jinja", title="Postings", count=count, totalCount=totalCount, offset=offset, postings=postings)

    @ControllerBase.authenticated(permissions=['user'])
    @ControllerBase.request("/upload", methods=["PUT"])
    def upload(self):
        log.debug("PostingController.upload(), request: %s", request)
        # check that request method is post
        if request.method != "PUT":
            return {"status": "error", "message": "Method not allowed"}
        # get json from request
        data = request.json
        # check that id is uuid
        try:
            id = uuid.UUID(data['id'])
        except ValueError:
            return {"status": "error", "message": "Invalid id"}
        # check that html is not empty
        if not 'html' in data or not isinstance(data['html'], str) or len(data['html']) == 0:
            return {"status": "error", "message": "Empty html"}
        # log the json
        app = current_app.instance()
        log.debug("pageLoad: %s (%d bytes)", data['id'], len(data['html']))
        postingsDir = os.path.join(app.storage.dataPath, "postings")
        postingRawHtmlDir = os.path.join(postingsDir, str(id) + ".raw.html")
        with open(postingRawHtmlDir, "w") as f:
            f.write(data['html'])
        dbRecord = models.Posting(id=str(id), url = data['url'])

        app.storage.dbSession.add(dbRecord)
        app.storage.dbSession.commit()
        app.tasks.add_task(lambda id=id: scraping.process_posting(id, app))
        # return json with status ok
        return {"status": "ok"}

    @ControllerBase.request("/uploadPrepare", methods=["PUT"])
    def uploadPrepare(self):
        log.debug("PostingController.uploadPrepare(), request: %s", request)
        if request.method != "PUT":
            return {"status": "error", "message": "Method not allowed"}
        # get json from request
        data = request.json
        log.debug("preparePageLoad: %s", data['url'])
        return {"status": "ok", "id": uuid.uuid4()}

    @ControllerBase.request("/uploadStatus")
    def uploadStatus(self):
        log.debug("PostingController.uploadStatus(), request: %s", request)
        if "id" not in request.args:
            return "Missing id parameter", 400
        try:
            id = uuid.UUID(request.args["id"])
        except ValueError:
            return "Invalid id", 400
        app = current_app.instance()
        postingsDir = app.storage.postingsPath
        postingPath = os.path.join(postingsDir, str(id) + ".raw.html")
        if os.path.exists(postingPath):
            return {"status": "waiting"}
        if os.path.exists(postingPath + ".error"):
            return {"status": "error"}
        return {"status": "ok"}

    @ControllerBase.request("/rescrape/<id>")
    def rescrape(self, id):
        try:
            id = uuid.UUID(id)
        except ValueError:
            return "Invalid id", 400
        app = current_app.instance()
        postingsDir = app.storage.postingsPath
        processedPath = os.path.join(postingsDir, str(id) + ".processed.html")
        rawPath = os.path.join(postingsDir, str(id) + ".raw.html")
        if not os.path.exists(rawPath) and not os.path.exists(processedPath):
            return {"status": "error", "message": "Raw file not found"}, 404
        if not os.path.exists(rawPath):
            os.rename(processedPath, rawPath)
        app.tasks.add_task(lambda id=id: scraping.process_posting(id, app))
        return {"status": "ok"}

    @ControllerBase.request("/item/<id>")
    def item(self, id):
        try:
            id = uuid.UUID(id)
        except ValueError:
            return "Invalid id", 400
        app = current_app.instance()
        posting = app.storage.dbSession.query(models.Posting).filter(models.Posting.id == str(id)).one()
        if not posting:
            return "Not found", 404
        posting = models.PostingRepresenter.fromAlchemy(posting)
        if request.content_type == "application/json":
            return jsonify(posting)
        return render_page("posting.html.jinja", title="Posting", header="Posting", posting=posting)


class ProfileController(ControllerBase):
    __prefix__ = "/trueapi/profile"

    # @staticmethod
    # def register(app: Flask):
    #     prefix = "/api/profile"
    #     log.debug("Registering ProfileController")
    #     def profileIndexHandler():
    #         return ProfileController().index()
    #     app.route(prefix)(profileIndexHandler)

    #     def profileItemHandler(id):
    #         return ProfileController().item(id)
    #     app.route(prefix + "/<id>")(profileItemHandler)

    #     def profileEditHandler(id):
    #         return ProfileController().edit(id)
    #     app.route(prefix + "/<id>/edit", methods=['GET', 'PUT'])(profileEditHandler)



    @ControllerBase.request("/items")
    def index(self):
        log.debug(f"{self.__class__.__name__}.index(), request: {request}")
        from  copilot.application import Application
        app = Application.instance()
        # app = copilotApp()
        profiles = {}
        for filename in os.listdir(app.storage.profilesPath):
            if filename.endswith(".json"):
                itemKey = filename.replace(".json", "")
                with open(os.path.join(app.storage.profilesPath, filename), "r") as f:
                    profiles[itemKey] = models.Profile.model_validate_json(f.read())
        resp = {key: prof.dict() for key, prof in profiles.items()}
        log.debug(f"{self.__class__.__name__}.index(), response: {resp}")
        return jsonify(resp)

    @ControllerBase.request("/item/<id>")
    def item(self, id):
        app = current_app.instance()
        profilePath = os.path.join(app.storage.profilesPath, f'{id}.json')
        if not os.path.exists(profilePath):
            return "Not found", 404
        profile = None
        with open(profilePath, 'r') as f:
            profile = models.Profile.model_validate_json(f.read())
        return render_page("profile.html.jinja", profileId = id, profile = profile)

    @ControllerBase.request("/update/<id>", methods=['PUT'])
    def edit(self, id):
        app = current_app.instance()
        profilePath = os.path.join(app.storage.profilesPath, f'{id}.json')
        if not os.path.exists(profilePath):
            return "Not found", 404
        profile = None
        with open(profilePath, 'r') as f:
            profile = models.Profile.model_validate_json(f.read())
        return render_page("profile-edit.html.jinja", profileId = id, profile = profile)
