import json
import os
from dotenv import load_dotenv
import google.genai as genai
from schemas.post_transcript_schema_florida import PostTranscriptStructuredOutputFlorida
from utils.env_loader import resource_path
env_path = resource_path(".env")
load_dotenv(env_path)

from schemas import (
    TranscriptStructuredOutput,
    PostTranscriptStructuredOutput,
    NoticeComparisonResult,
    RbComparisonResult,
    OtherNoticeComparisonResult,
    TitleComparisonResult,
    ExhibitMatchResponse
)

class LLMExtractor:
    """
    Gemini-based extractor for legal transcript metadata.
    """

    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL_NAME")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")

        if not self.model_name:
            raise ValueError("GEMINI_MODEL_NAME not set")

        self.client = genai.Client(api_key=self.api_key)

    # --------------------------------------------------
    # Pre-transcript extraction
    # --------------------------------------------------

    def extract_pre_transcript(
        self,
        prompt: str,
        text: str,
    ) -> dict:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt + "\n" + text,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": TranscriptStructuredOutput.model_json_schema(),
            },
        )
        return json.loads(response.text)

    # --------------------------------------------------
    # Post-transcript extraction
    # --------------------------------------------------

    def extract_post_transcript(
        self,
        prompt: str,
        text: str,
    ) -> dict:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt + "\n" + text,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": PostTranscriptStructuredOutput.model_json_schema(),
            },
        )
        return json.loads(response.text)
    
    def extract_notice_comparison(
        self,
        prompt: str,
        dict_to_compare: str,
        notice_data: str
    ) -> dict:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt + "\n" + dict_to_compare + "\n" + notice_data,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": NoticeComparisonResult.model_json_schema(),
            },
        )
        return json.loads(response.text)
    
    def extract_rb_comparison(
        self,
        prompt: str,
        dict_to_compare: str,
        rb_data: str
    ) -> dict:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt + "\n" + "\n" + str(dict_to_compare) + "\n" + "\n" + str(rb_data),
            config={
                "response_mime_type": "application/json",
                "response_json_schema": RbComparisonResult.model_json_schema(),
            },
        )
        return json.loads(response.text)
    
    def extract_other_notice_comparison(
        self,
        prompt: str,
        dict_to_compare: str,
        notice_data: str
    ) -> dict:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt + "\n" + dict_to_compare + "\n" + notice_data,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": OtherNoticeComparisonResult.model_json_schema(),
            },
        )
        return json.loads(response.text)   


    def extract_post_transcript_florida(
        self,
        prompt: str,
        text: str,
    ) -> dict:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt + "\n" + text,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": PostTranscriptStructuredOutputFlorida.model_json_schema(),
            },
        )
        return json.loads(response.text) 
    
    def extract_title_comparison(
        self,
        prompt: str,
        dict_to_compare: str
    ) -> dict:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt + "\n" + dict_to_compare + "\n",
            config={
                "response_mime_type": "application/json",
                "response_json_schema": TitleComparisonResult.model_json_schema(),
            },
        )
        return json.loads(response.text)
    
    def extract_exhibit_comparison(
        self,
        prompt: str,
        exhibit_filenames: list[str],
        exhibit_names_list: list[str]
    ) -> dict:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt + "\n" + json.dumps(exhibit_filenames) + "\n" + json.dumps(exhibit_names_list),
            config={
                "response_mime_type": "application/json",
                "response_json_schema": ExhibitMatchResponse.model_json_schema(),
            },
        )
        return json.loads(response.text)

