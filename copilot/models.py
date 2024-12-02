
from pydantic import BaseModel, ValidationError, WrapValidator
from dataclasses import dataclass
import pydantic_core
from typing import Deque, List, Optional, Tuple, Any
import uuid
import copilot.intelligence as intelligence
from typing_extensions import Annotated
import datetime as dt
import logging
log = logging.getLogger(__name__)





class Contact(BaseModel):
    type: str
    value: str

class Experience(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: str
    description: str
    technologies: List[str]

class Education(BaseModel):
    school: str
    degree: str
    start_date: str
    end_date: str
    description: Optional[str] = None

class Profile(BaseModel):
    name: str
    title: str
    description: str
    contacts: List[Contact]
    strengths: List[str]
    skills: List[str]
    achievements: List[str]
    experiences: List[Experience]
    educations: List[Education]


import sqlalchemy as SQA
import sqlalchemy.orm as ORM

class DeclBase(ORM.DeclarativeBase):
    pass


class PostingIntelligence(BaseModel):
    company_name: str
    canonical_job_title: str
    brief_description: str
    technology_stack: List[str]
    salary_range: str
    responsibility_level: str
    rush_level: str
    bullshit_job: bool
    location: str
    remote: bool
    hybrid: bool
    onsite: bool
    hard_to_pass: bool
    fixed_term: bool
    seniority_level: str
    employment_type: str
    language_requirements: str
    application_deadline_date: str
    posted_at_date: str
    company_industry: str
    company_size: str
    benefits: List[str]
    job_cons: List[str]
    job_pros: List[str]
    brief_jobseeker_advice: str

class PostingIntelligenceRepresenter(PostingIntelligence):
    @classmethod
    def from_json(cls, data: dict, allow_partial: bool = False):
        try:
            return cls.model_construct(**pydantic_core.from_json(data, allow_partial=allow_partial))
        except:
            log.exception(f"Failed to parse data: {data}")

class Posting(DeclBase):
    __tablename__ = "postings"
    id: uuid.UUID = SQA.Column(SQA.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # UUID as TEXT
    company: str = SQA.Column(SQA.String)
    title: str = SQA.Column(SQA.String)
    url: str = SQA.Column(SQA.String)
    description: str = SQA.Column(SQA.String)
    skills: str = SQA.Column(SQA.String)
    posted_at: str = SQA.Column(SQA.DateTime)
    deadline_at: str = SQA.Column(SQA.DateTime)
    added_at: str = SQA.Column(SQA.DateTime, default=SQA.func.now())
    duplicate: bool = SQA.Column(SQA.Boolean, default=False)
    intelligence: str = SQA.Column(SQA.String)

class PostingRepresenter(BaseModel):
    id: uuid.UUID
    company: str
    title: str
    url: str
    description: str
    skills: List[str]
    posted_at: dt.datetime
    deadline_at: dt.datetime
    added_at: dt.datetime
    duplicate: bool
    intelligence: PostingIntelligenceRepresenter


    @staticmethod
    def fromAlchemy(posting: Posting):
        return PostingRepresenter.model_construct(
            id=posting.id,
            company=posting.company,
            title=posting.title,
            url=posting.url,
            description=posting.description,
            skills=posting.skills.split(", "),
            posted_at=posting.posted_at,
            deadline_at=posting.deadline_at,
            added_at=posting.added_at,
            duplicate=posting.duplicate,
            intelligence=PostingIntelligenceRepresenter.from_json(posting.intelligence, allow_partial=True)
        )

