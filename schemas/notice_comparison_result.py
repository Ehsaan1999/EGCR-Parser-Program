from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class MatchResult(str, Enum):
    EXACT_MATCH = "Exact Match"
    PARTIAL_MATCH = "Partial Match"
    NO_MATCH = "No Match"
    MISSING = "Missing"

class NoticeComparisonResult(BaseModel):
    court_heading: Optional[MatchResult] = Field(description="Comparison result for court heading")
    case_number: Optional[MatchResult] = Field(description="Comparison result for case number")
    case_style: Optional[MatchResult] = Field(description="Comparison result for case style")
    job_title: Optional[MatchResult] = Field(description="Comparison result for job title")
    witness_name: Optional[MatchResult] = Field(description="Comparison result for witness name")
    job_date: Optional[MatchResult] = Field(description="Comparison result for date")
    start_time: Optional[MatchResult] = Field(description="Comparison result for start time")
    location: Optional[str] = Field(description="Comparison result for location")
    
    # Indexed Attorney/Firm Fields
    attorney_names_1: Optional[MatchResult] = Field(description="Match for first attorney")
    attorney_names_2: Optional[MatchResult] = Field(description="Match for second attorney")
    attorney_names_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining attorneys")
    
    attorney_representation_1: Optional[MatchResult] = Field(description="Match for first representation")
    attorney_representation_2: Optional[MatchResult] = Field(description="Match for second representation")
    attorney_representation_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining")
    
    firm_names_1: Optional[MatchResult] = Field(description="Match for first firm")
    firm_names_2: Optional[MatchResult] = Field(description="Match for second firm")
    firm_names_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining firms")
    
    firm_address_1: Optional[MatchResult] = Field(description="Match for first address")
    firm_address_2: Optional[MatchResult] = Field(description="Match for second address")
    firm_address_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining addresses")

    firm_city_1: Optional[MatchResult] = Field(description="Match for first city")
    firm_city_2: Optional[MatchResult] = Field(description="Match for second city")
    firm_city_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining cities")

    firm_state_1: Optional[MatchResult] = Field(description="Match for first state")
    firm_state_2: Optional[MatchResult] = Field(description="Match for second state")
    firm_state_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining states")

    firm_zip_1: Optional[MatchResult] = Field(description="Match for first zip")
    firm_zip_2: Optional[MatchResult] = Field(description="Match for second zip")
    firm_zip_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining zips")

    phone_numbers_1: Optional[MatchResult] = Field(description="Match for first phone")
    phone_numbers_2: Optional[MatchResult] = Field(description="Match for second phone")
    phone_numbers_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining phones")

    emails_1: Optional[MatchResult] = Field(description="Match for first email")
    emails_2: Optional[MatchResult] = Field(description="Match for second email")
    emails_cont: Optional[str] = Field(description="Fractional match (X/Y) for remaining emails")

    transcript_job_title: Optional[MatchResult] = Field(description="Comparison result for transcript job heading")
    transcript_witness_name: Optional[MatchResult] = Field(description="Comparison result for transcript witness name")
    index_witness_name: Optional[MatchResult] = Field(description="Comparison result for index witness name")
    transcript_date: Optional[MatchResult] = Field(description="Comparison result for first page of transcript date")
    disclosure_date: Optional[MatchResult] = Field(description="Comparison result for disclosure page date")
    certificate_date: Optional[MatchResult] = Field(description="Comparison result for certificate page date")
    oath_certificate_page_date: Optional[MatchResult] = Field(description="Comparison for Florida oath date")