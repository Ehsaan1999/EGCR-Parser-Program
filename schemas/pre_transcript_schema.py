from typing import List, Optional
from pydantic import BaseModel, Field

class PageReference(BaseModel):
    page: str = Field(description="The corresponding page number")
    name: str = Field(description="The title or description of the item")

class TranscriptStructuredOutput(BaseModel):
    # ---------------- Page 1: Title Page ----------------
    court_heading: Optional[str] = Field(description="Court heading text")
    case_number: Optional[str] = Field(description="Case number")
    case_style: Optional[str] = Field(description="Case style")
    job_title: Optional[str] = Field(description="Job title such as 'Deposition of'")
    witness_name: Optional[str] = Field(description="Witness name on title page")
    job_date: Optional[str] = Field(description="Date on title page")
    current_date: Optional[str] = Field(description="The specific current date provided in the instructions.")
    start_time: Optional[str] = Field(description="Start time")
    location: Optional[str] = Field(description="Full city name or full remote parenthetical")
    resource: Optional[str] = Field(description="Resource name only")

    # ---------------- Page 2: First Appearance ----------------

    appearances_present: bool = Field(
        description="True if 'Index to Appearances' heading exists"
    )
    esquire_check_1: Optional[str] = Field(
        description="Returns if 'Esquire's present after Attorney name"
    )
    attorney_representation_1: Optional[str] = Field(
        description="List of attorneys with their 'On behalf of the Plaintiff/Defendant/etc.'"
    )
    attorney_names_1: Optional[str] = Field(
        description="Attorney names listed under appearances"
    )
    firm_names_1: Optional[str] = Field(
        description="Firm names"
    )
    firm_address_1: Optional[str] = Field(
        description="Firm addresses"
    )
    firm_city_1: Optional[str] = Field(
        description="Firm city"
    )
    firm_state_1: Optional[str] = Field(
        description="Firm state"
    )
    firm_zip_1: Optional[str] = Field(
        description="Firm zip code"
    )
    phone_numbers_1: Optional[str] = Field(
        description="Phone numbers found"
    )
    emails_1: Optional[str] = Field(
        description="Email addresses found"
    )

    # ---------------- Page 2: Second Appearance ----------------
    
    esquire_check_2: Optional[str] = Field(
        description="Returns if 'Esquire's present after Attorney name"
    )
    attorney_representation_2: Optional[str] = Field(
        description="List of attorneys with their 'On behalf of the Plaintiff/Defendant/etc.'"
    )
    attorney_names_2: Optional[str] = Field(
        description="Attorney names listed under appearances"
    )
    firm_names_2: Optional[str] = Field(
        description="Firm names"
    )
    firm_address_2: Optional[str] = Field(
        description="Firm addresses"
    )
    firm_city_2: Optional[str] = Field(
        description="Firm city"
    )
    firm_state_2: Optional[str] = Field(
        description="Firm state"
    )
    firm_zip_2: Optional[str] = Field(
        description="Firm zip code"
    )
    phone_numbers_2: Optional[str] = Field(
        description="Phone numbers found"
    )
    emails_2: Optional[str] = Field(
        description="Email addresses found"
    )

    # ---------------- Page 2: Appearances Continued ----------------
    
    esquire_check_cont: Optional[str] = Field(
        description="Returns number of 'Esquire's present after Attorney name"
    )
    attorney_representation_cont: Optional[str] = Field(
        description="List of attorneys with their 'On behalf of the Plaintiff/Defendant/etc.'"
    )
    attorney_names_cont: Optional[list[str]] = Field(
        description="Attorney names listed under appearances"
    )
    firm_names_cont: Optional[list[str]] = Field(
        description="Firm names"
    )
    firm_address_cont: Optional[list[str]] = Field(
        description="Firm addresses"
    )
    firm_city_cont: Optional[list[str]] = Field(
        description="Firm city"
    )
    firm_state_cont: Optional[list[str]] = Field(
        description="Firm state"
    )
    firm_zip_cont: Optional[list[str]] = Field(
        description="Firm zip code"
    )
    phone_numbers_cont: Optional[list[str]] = Field(
        description="Phone numbers found"
    )
    emails_cont: Optional[list[str]] = Field(
        description="Email addresses found"
    )

    # ---------------- Page 3: Index Page ----------------

    index_witness_name: Optional[str] = Field(
        description="Witness name as shown in index page"
    )
    index_to_examinations_proceedings_present: bool = Field(
        description="True if 'Index to Examinations/Proceedings' heading exists"
    )
    index_to_examinations_proceedings_heading: Optional[str] = Field(
        description="Text of Index to Examinations/Proceedings heading"
    )
    index_to_exhibits_present: bool = Field(
        description="True if 'Index to Exhibits' heading exists"
    )
    index_to_exhibits_heading: Optional[str] = Field(
        description="Text of Index to Exhibits heading"
    )
    index_to_exhibits_retained: Optional[bool] = Field(
        description="True if Index to Exhibits information is retained in the transcript"
    )
    examinations_proceedings_page_numbers: Optional[List[PageReference]] = Field(
        description="List of all pages with Examinations/Proceedings"
    )
    exhibits_page_numbers: Optional[List[PageReference]] = Field(
        description="List of all pages with exhibits"
    )
    exhibit_parenthetical: Optional[str] = Field(
        description="Text within exhibit parenthetical"
    )

    # ---------------- Page 4: Transcript First Page ----------------

    transcript_job_title: Optional[str] = Field(
        description="Returns job heading from Transcript Page 1"
    )
    transcript_witness_name: Optional[str] = Field(
        description="Witness name as shown at the beginning of the transcript"
    )
    transcript_date: Optional[str] = Field(
        description="Date at the beginning of the transcript"
    )
    duly_sworn: bool = Field(
        description="True if witness was duly sworn at the beginning of the transcript"
    )