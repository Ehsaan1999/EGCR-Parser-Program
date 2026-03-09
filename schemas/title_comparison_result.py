from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class MatchResult(str, Enum):
    EXACT_MATCH = "Exact Match"
    PARTIAL_MATCH = "Partial Match"
    NO_MATCH = "No Match"
    MISSING = "Missing"

class TitleComparisonResult(BaseModel):
    
    transcript_job_title: Optional[str] = Field(
        description="Job heading match from Transcript Page 1 to Title Page"
    )
    index_to_examinations_proceedings_heading_check: Optional[str] = Field(
        description="Index to Examinations/Proceedings heading match from Index Page to Title Page"
    )
    index_witness_name: Optional[str] = Field(
        description="Witness name match from Index Page to Title Page"
    )
    transcript_witness_name: Optional[str] = Field(
        description="Witness name match from Transcript Page 1 to Title Page"
    )
    transcript_date: Optional[str] = Field(
        description="Date match from Transcript Page 1 to Title Page"
    )