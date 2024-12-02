
import logging

log = logging.getLogger(__name__)

from flask import Flask, request, current_app, jsonify

from copilot.views import render_page


import copilot.scraping as scraping
import copilot.models as models
import uuid

import os


class ControllerBase:
    def __init__(self):
        pass

    @staticmethod
    def register(app: Flask):
        log.debug("Registering ControllerBase")
        HomeController.register(app)
        PostingController.register(app)
        ProfileController.register(app)

class HomeController:
    def __init__(self):
        pass

    @staticmethod
    def register(app: Flask):
        log.debug("Registering HomeController")
        def homeHandler():
            return HomeController().home()
        app.route("/")(homeHandler)
        # def profileHandler():
            # return HomeController().profile()
        # app.route("/profile")(profileHandler)

    def home(self):
        log.debug("HomeController.hello_world(), request: %s", request)
        return render_page("home.html.jinja", title="Home", header="Hello, world!")


    # def profile(self):
    #     log.debug("HomeController.profile(), request: %s", request)
    #     return render_page("profile.html.jinja", title="Profile", header="Profile Page", profile=profile)



class PostingController:
    def __init__(self):
        pass

    @staticmethod
    def register(app: Flask):
        prefix = "/posting"
        log.debug("Registering PostingController")
        def indexHandler():
            return PostingController().index()
        app.route(prefix)(indexHandler)

        def uploadHandler():
            return PostingController().upload()
        app.route(prefix + "/upload", methods=["PUT"])(uploadHandler)

        def uploadPrepareHandler():
            return PostingController().uploadPrepare()
        app.route(prefix + "/uploadPrepare", methods=["PUT"])(uploadPrepareHandler)

        def uploadStatusHandler():
            return PostingController().uploadStatus()
        app.route(prefix + "/uploadStatus")(uploadStatusHandler)

        def itemHandler(id):
            return PostingController().item(id)
        app.route(prefix + "/item/<id>")(itemHandler)

        def rescrapeHandler(id):
            return PostingController().rescrape(id)
        app.route(prefix + "/rescrape/<id>")(rescrapeHandler)

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

    def uploadPrepare(self):
        log.debug("PostingController.uploadPrepare(), request: %s", request)
        if request.method != "PUT":
            return {"status": "error", "message": "Method not allowed"}
        # get json from request
        data = request.json
        log.debug("preparePageLoad: %s", data['url'])
        return {"status": "ok", "id": uuid.uuid4()}

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


class ProfileController:
    def __init__(self):
        pass

    @staticmethod
    def register(app: Flask):
        prefix = "/profile"
        log.debug("Registering ProfileController")
        def profileIndexHandler():
            return ProfileController().index()
        app.route(prefix)(profileIndexHandler)

    def index(self):
        log.debug("ProfileController.profile(), request: %s", request)
        app = current_app.instance()
        # get profile files
        profiles = {}
        for filename in os.listdir(app.storage.profilesPath):
            if filename.endswith(".json"):
                with open(os.path.join(app.storage.profilesPath, filename), "r") as f:
                    profiles[filename] = models.Profile.model_validate_json(f.read())
        resp = {key: prof.dict() for key, prof in profiles.items()}
        return jsonify(resp)