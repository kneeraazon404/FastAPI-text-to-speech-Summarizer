# models.py
from pydantic import BaseModel


class SummaryInput(BaseModel):
    summary: str


class Transcription:
    table = "transcriptions"
    id = "id"
    summary = "summary"
    transcription = "transcription"
    language_code = "language_code"
