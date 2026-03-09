from enum import Enum
from typing import Dict
from pydantic import BaseModel, Field

class MatchStatus(str, Enum):
    EXACT_MATCH = "Exact Match"
    PARTIAL_MATCH = "Partial Match"
    NO_MATCH = "No Match"
    MISSING = "Missing"


class ExhibitMatchResponse(BaseModel):
    # This will return: {"Exhibit 1": "Exact Match", "Exhibit 2": "No Match"}
    comparisons: Dict[str, MatchStatus] = Field(
        description="A dictionary mapping each transcript exhibit name to its match status against the provided filenames."
    )