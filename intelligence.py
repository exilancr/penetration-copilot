


import settings
import logging
import os
from copilot.intelligence import register_intelligence, ExperienceModel, tuneExperienceDescription



class MyApp:
    def __init__(self, settings):
        self.settings = settings
        self.debug = False
        self.intelligence = None

app = MyApp(settings)

app.debug = settings.DEBUG if hasattr(settings, "DEBUG") else False
logName = __name__
if logName == "__main__":
    logName = os.path.basename(__file__)

logFormat = "%(asctime)s [%(levelname)s] %(name)s %(message)s"
logLevel = logging.INFO
if app.debug:
    logLevel = logging.DEBUG
logging.basicConfig(format=logFormat, level=logLevel)

log = logging.getLogger(logName)

register_intelligence(app)

log.info("Checking intelligence")

jobDescription = '''
# Job Title: Senior Full Stack Developer

## Candidate Requirements:
- **Experience**: Minimum 7 years in demanding software development projects.
- **Skills**:
  - Proficiency in JavaScript/TypeScript, React, Node.js, or Java.
  - Experience with cloud platforms such as Azure, GCP, or AWS.
- **Attributes**:
  - Strong problem-solving skills and a can-do attitude.
  - Self-driven and proactive with a desire to learn new technologies.
  - Fluent in Finnish and proficient in English.
- **Culture Fit**:
  - Enthusiastic and collaborative team player.
  - Committed to delivering high-quality solutions for clients.

## Benefits:
- Opportunity to grow expertise in diverse client projects.
- Supportive and flexible work environment.
- Hybrid work model and extensive employee benefits.
'''

shortJobRequirements = '''
Job Title: Full Stack Developer

Technologies: JavaScript, TypeScript, React, Node.js, Java, Cloud technologies (Azure, GCP, AWS)
'''
experienceItem = app.settings.profile["experiences"][0]
experience = ExperienceModel(description=experienceItem["description"], technologies=experienceItem["technologies"])

result = tuneExperienceDescription(app, experience, shortJobRequirements, comment="Be short, it is a CV version. ")
print("Result:")

print("Description:")
print(result.description)
print("Technologies:")
print(', '.join(result.technologies))