
from openai import OpenAI
from pydantic import BaseModel


from typing import List, NewType
from copilot import models

import datetime as dt


import logging

log = logging.getLogger(__name__)


class ExperienceModel(BaseModel):
    description: str
    technologies: List[str]

def promptAsModel(client, model, prompts: List[str]):
    expectedFields = ', '.join([f"{k} - {v}" for k, v in model.model_fields.items()])
    log.info(expectedFields)
    messages = []
    messages.append({"role": "system", "content": f"Fill in the following fields: {expectedFields}"})
    for prompt in prompts:
        messages.append({"role": "user", "content": prompt})
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=model,

    )
    resultMessage = response.choices[0].message
    log.debug("Result: %s", resultMessage)
    return resultMessage.parsed



def register_intelligence(app):
    if app.settings.openaiApiKey is None or app.settings.openaiApiKey == "":
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")
    app.intelligence = OpenAI(
        api_key=app.settings.openaiApiKey,
    )
    log.info("Intelligence registered")


def tuneExperienceDescription(app, experience: ExperienceModel, jobDescription: str, comment: str):
    prompts = [
        f"""
Having an item of working experience, reorganize it to align and match better with job posting requirements.
Keep the structure.
{comment}
Output format is markdown.
        """,
        f"Experience:\n {experience.description}\nTechnologies: {', '.join(experience.technologies)}",
        f"Job posting information:\n{jobDescription}",
    ]
    return promptAsModel(app.intelligence, ExperienceModel, prompts)





def extractPostingInformation(app, jobDescription: str):
    outModel = models.PostingIntelligence
    expectedFields = ', '.join([f"{k} - {v}" for k, v in outModel.model_fields.items()])
    prompts = [
        f"Based on a provided job description, give requested data. Use markdown to format text if needed. Result language is English. Format date/time in ISO 8601.",
        f"Job description:\n{jobDescription}"
    ]
    return promptAsModel(app.intelligence, outModel, prompts)