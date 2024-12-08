import logging

log = logging.getLogger(__name__)
import uuid
import os
import time
from dateutil import parser as dateparser
import datetime as dt
import copilot.models as models
from copilot.storage import Storage
from copilot.intelligence import extractPostingInformation


import bs4


def process_posting(id: uuid.UUID, app):
    log.debug(f"Processing posting {id}")
    storage: Storage = app.storage
    dbRecord: models.Posting = storage.dbSession.query(models.Posting).get(str(id))
    postingPath = os.path.join(storage.postingsPath, str(id) + ".raw.html")
    if not os.path.exists(postingPath):
        log.error("Posting not found: {postingPath}")
        return
    if dbRecord is None:
        log.error("Posting not found in database {id}")
        os.rename(postingPath, postingPath + ".error")
        return
    log.debug(f"Extracting description for posting {id}")
    extractor = get_extractor(dbRecord.url)
    if extractor is None:
        log.error(f"Extractor not found for url: {dbRecord.url}")
        os.rename(postingPath, postingPath + ".error")
        return
    with open(postingPath, "r") as f:
        soup = bs4.BeautifulSoup(f.read(), "html.parser")
    extractedText = extractor(soup)
    with open(os.path.join(storage.postingsPath, str(id) + ".dump"), "w") as f:
        f.write("### Extraction\n")
        f.write(extractedText)

    extractedText = extractedText.replace("\n\n", "\n")
    extractedText = extractedText.strip()
    extractedText = extractedText[:5000]

    log.debug(f"Requesting intelligence for posting {id}")

    intelligenceData = extractPostingInformation(app, extractedText)

    with open(
        os.path.join(storage.postingsPath, str(id) + ".intelligence.json"), "w"
    ) as f:
        f.write(intelligenceData.model_dump_json(indent=4))

    log.debug(f"Saving intelligence for posting {id}")

    dbRecord.description = intelligenceData.brief_description
    dbRecord.company = intelligenceData.company_name
    dbRecord.title = intelligenceData.canonical_job_title
    dbRecord.skills = ", ".join(intelligenceData.technology_stack)
    try:
        dbRecord.posted_at = dateparser.parse(intelligenceData.posted_at_date)
    except:
        pass
    try:
        dbRecord.deadline_at = dateparser.parse(intelligenceData.application_deadline_date, default = None)
    except:
        pass
    dbRecord.intelligence = intelligenceData.model_dump_json(indent=None)

    storage.dbSession.commit()
    log.debug(f"Rename {postingPath} to {str(id)}.processed.html")
    os.rename(
        postingPath, os.path.join(storage.postingsPath, str(id) + ".processed.html")
    )

    log.debug(f"Marking duplicates for {dbRecord.url}")
    postings = (
        storage.dbSession.query(models.Posting)
        .filter(models.Posting.url == dbRecord.url)
        .filter(models.Posting.id != dbRecord.id)
        .all()
    )
    for posting in postings:
        posting.duplicate = True
    storage.dbSession.commit()

    log.debug(f"Pocessing posting {id} done")


def get_extractor(url):
    if "tyomarkkinatori" in url:
        return tyomarkkinatori_extractor
    return None


def tyomarkkinatori_extractor(soup):
    mainTag = soup.find("main")
    mainTagText = mainTag.get_text(separator="\n")
    return mainTagText


def register_scraping(app):
    log.debug("Registering scraping")
    process_postings(app)


def process_postings(app):
    storage = app.storage
    log.debug("Processing postings")
    for filename in os.listdir(storage.postingsPath):
        if filename.endswith(".raw.html"):
            id = uuid.UUID(filename.removesuffix(".raw.html"))
            app.tasks.add_task(lambda id=id: process_posting(id, app))
