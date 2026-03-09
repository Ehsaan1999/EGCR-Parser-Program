from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class MatchResult(str, Enum):
    EXACT_MATCH = "Exact Match"
    PARTIAL_MATCH = "Partial Match"
    NO_MATCH = "No Match"
    MISSING = "Missing"

class OtherNoticeComparisonResult(BaseModel):
    court_heading: Optional[MatchResult] = Field(description="Comparison result for court heading")
    case_number: Optional[MatchResult] = Field(description="Comparison result for case number")
    case_style: Optional[MatchResult] = Field(description="Comparison result for case style")
    job_date: Optional[MatchResult] = Field(description="Comparison result for date")
    location: Optional[str] = Field(description="Comparison result for location")
    
    # Indexed Attorney/Firm Fields
    attorney_names_1: Optional[MatchResult] = Field(description="Match for first attorney")
    attorney_names_2: Optional[MatchResult] = Field(description="Match for second attorney")
    attorney_names_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining")
    
    firm_names_1: Optional[MatchResult] = Field(description="Match for first firm")
    firm_names_2: Optional[MatchResult] = Field(description="Match for second firm")
    firm_names_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining")
    
    firm_address_1: Optional[MatchResult] = Field(description="Match for first address")
    firm_address_2: Optional[MatchResult] = Field(description="Match for second address")
    firm_address_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining")

    firm_city_1: Optional[MatchResult] = Field(description="Match for first city")
    firm_city_2: Optional[MatchResult] = Field(description="Match for second city")
    firm_city_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining")

    firm_state_1: Optional[MatchResult] = Field(description="Match for first state")
    firm_state_2: Optional[MatchResult] = Field(description="Match for second state")
    firm_state_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining")

    firm_zip_1: Optional[MatchResult] = Field(description="Match for first zip")
    firm_zip_2: Optional[MatchResult] = Field(description="Match for second zip")
    firm_zip_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining")