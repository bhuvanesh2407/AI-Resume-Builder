from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import date
import json
from dataclasses import fields, is_dataclass
from typing import get_origin, get_args

# -----------------------
# Generic dict -> dataclass converter
# -----------------------
def from_dict(cls, data: dict):
    if not is_dataclass(cls):
        return data

    kwargs = {}
    for f in fields(cls):
        value = data.get(f.name)
        if value is None:
            kwargs[f.name] = None
            continue

        field_type = f.type
        origin = get_origin(field_type)

        # Handle List[...] types
        if origin == list:
            inner_type = get_args(field_type)[0]
            kwargs[f.name] = [from_dict(inner_type, item) for item in value]

        # Nested dataclass
        elif is_dataclass(field_type):
            kwargs[f.name] = from_dict(field_type, value)

        # For date field in Resume
        elif field_type == date:
            kwargs[f.name] = date.fromisoformat(value)

        else:
            kwargs[f.name] = value

    return cls(**kwargs)


@dataclass
class ProfessionalExperience:
    job_title: str
    company_name: str
    place: str
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    description: Optional[str] = None

    def formatted_title(self):
        return f"{self.job_title} | {self.company_name}, "

    def formatted_dates(self):
        return f"{self.from_date} - {self.to_date}"


@dataclass
class TechnicalProject:
    project_name: str
    description: Optional[str] = None


@dataclass
class Education:
    degree_name: str
    college_name: str
    place: str
    completed_on: Optional[str] = None
    result: Optional[str] = None
    description: Optional[str] = None

    def formatted_clg_details(self):
        return f'{self.college_name}, {self.place}'

    def formatted_dates(self):
        return f"{self.from_date} - {self.to_date}"


@dataclass
class Certification:
    title: str
    issuing_company: str
    completion_date: Optional[str] = None


@dataclass
class Resume:

    # Introduction
    name: str
    designation: str
    place: str
    emails: List[str] = field(default_factory=list)
    mobile_numbers: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    nationality: Optional[str] = None
    dob: Optional[date] = None
    visa_status: Optional[str] = None
    notice_period: Optional[str] = None
    profile_description: Optional[str] = None

    # Professional Info
    professional_summary: Optional[str] = None
    technical_skills: Optional[str] = None

    # Nested lists
    professional_experience: List[ProfessionalExperience] = field(default_factory=list)
    technical_projects: List[TechnicalProject] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)

    def to_dict(self):
        """Convert Resume to dict (including nested objects)."""
        return asdict(self)

    def to_json(self):
        """Convert Resume to JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=4)
    
    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return from_dict(cls, data)