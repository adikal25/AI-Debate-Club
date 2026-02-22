from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Claim(BaseModel):
    assertion: str
    evidence: str
    reasoning: str


class Argument(BaseModel):
    position: Literal["for", "against"]
    opening_statement: str
    claims: list[Claim]
    conclusion: str
    model_id: str = ""


class Score(BaseModel):
    category: Literal["logic", "evidence", "rhetoric"]
    score: int = Field(ge=1, le=10)
    justification: str


class Judgment(BaseModel):
    for_scores: list[Score]
    against_scores: list[Score]
    winner: Literal["for", "against", "tie"]
    reasoning: str
    model_id: str = ""


class DebateResult(BaseModel):
    topic: str
    for_argument: Argument
    against_argument: Argument
    judgment: Judgment
    timestamp: datetime = Field(default_factory=datetime.now)
