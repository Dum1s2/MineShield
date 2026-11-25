from typing import Literal
from pydantic import BaseModel, Field

ChannelType = Literal["telegram", "slack", "email"]
RiskLevel = Literal["low", "medium", "high"]


class ReasonItem(BaseModel):
    """Single human-readable signal explaining part of the risk score."""

    category: str = Field(..., description="Signal category, e.g. urgency, typosquatting, spf_fail")
    description: str = Field(..., description="Short user-facing explanation")
    evidence: str | None = Field(default=None, description="Matched snippet or domain")
    weight: float = Field(default=0.5, ge=0.0, le=1.0)


class AnalyzeRequest(BaseModel):
    """Unified input payload sent to both ml/ and sec/ modules."""

    text: str = Field(default="", description="Message or email body text")
    urls: list[str] = Field(default_factory=list, description="Extracted URLs from the message")
    channel: ChannelType = Field(default="telegram")
    headers: dict[str, str] = Field(
        default_factory=dict,
        description="Optional email headers (From, Reply-To, Authentication-Results)",
    )


class MLResult(BaseModel):
    """Output contract for the Data Science (ml/) module."""

    ml_score: float = Field(..., ge=0.0, le=1.0, description="Calibrated phishing probability")
    reasons: list[ReasonItem] = Field(default_factory=list)
    model_version: str = Field(default="0.1.0-mvp")


class SecResult(BaseModel):
    """Output contract for the InfoSec (sec/) module."""

    sec_score: float = Field(..., ge=0.0, le=1.0, description="Technical security risk score")
    reasons: list[ReasonItem] = Field(default_factory=list)
    checked_urls: list[str] = Field(default_factory=list)


class VerdictResponse(BaseModel):
    """Combined API response returned to bot/ or client."""

    risk_level: RiskLevel
    total_score: float = Field(..., ge=0.0, le=1.0)
    ml: MLResult
    sec: SecResult
    summary: str
