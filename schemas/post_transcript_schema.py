from typing import Optional
from pydantic import BaseModel, Field


class PostTranscriptStructuredOutput(BaseModel):
    # ---------------- End of Testimony ----------------
    end_time: Optional[str] = Field(
        description="Time testimony concluded (e.g., '11:06 a.m.')"
    )
    signature_status: Optional[str] = Field(
        description="Witness signature status: Waived or Reserved"
    )

    # ---------------- Disclosure Page ----------------
    disclosure_page_present: bool = Field(
        description="True if Disclosure page is present"
    )
    disclosure_heading: Optional[str] = Field(
        description="Returns Disclosure heading if present"
    )
    disclosure_date: Optional[str] = Field(
        description="Date listed on Disclosure page"
    )
    disclosure_resource_name: Optional[str] = Field(
        description="Court reporter or firm name on Disclosure page"
    )

    # ---------------- Certificate Page ----------------
    certificate_heading_present: bool = Field(
        description="True if Certificate heading exists"
    )
    certificate_heading: Optional[str] = Field(
        description="Returns Certificate heading if present"
    )
    court_subheading_present: bool = Field(
        description="True if court subheading exists"
    )
    court_subheading: Optional[str] = Field(
        description="Returns Court subheading if present"
    )
    certificate_date: Optional[str] = Field(
        description="Date listed on Certificate page"
    )
    certificate_resource_name: Optional[str] = Field(
        description="Court reporter name on Certificate page"
    )
