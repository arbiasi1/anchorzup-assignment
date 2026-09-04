from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Keyword = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]


class RuleFields(BaseModel):
    keyword: Keyword
    match_type: Literal["contains", "startsWith", "exact"]
    action_type: Literal["highlight", "tooltip"]
    color: str | None = None
    label: str | None = Field(default=None, max_length=100)
    priority: int = Field(default=0, ge=0, le=100)
    enabled: bool = True
    case_sensitive: bool = False

    @model_validator(mode="after")
    def validate_action(self):
        if self.action_type == "highlight":
            self.color = self.color or "#facc15"
            if not __import__("re").fullmatch(r"#[0-9a-fA-F]{6}", self.color):
                raise ValueError("color must be a six-digit hex color")
            self.label = None
        else:
            self.label = (self.label or "Match").strip()
            if not self.label:
                raise ValueError("tooltip label cannot be empty")
            self.color = None
        return self


class RuleCreate(RuleFields):
    pass


class RuleUpdate(BaseModel):
    keyword: Keyword | None = None
    match_type: Literal["contains", "startsWith", "exact"] | None = None
    action_type: Literal["highlight", "tooltip"] | None = None
    color: str | None = None
    label: str | None = Field(default=None, max_length=100)
    priority: int | None = Field(default=None, ge=0, le=100)
    enabled: bool | None = None
    case_sensitive: bool | None = None


class RuleOut(RuleFields):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProcessRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)


class MatchInfo(BaseModel):
    rule_id: int
    keyword: str
    action_type: str
    color: str | None
    label: str | None
    priority: int


class TextSegment(BaseModel):
    text: str
    matches: list[MatchInfo]


class ProcessResponse(BaseModel):
    segments: list[TextSegment]
    match_count: int
    matched_rule_count: int

