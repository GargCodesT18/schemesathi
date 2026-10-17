"""Evaluation Result Models for SchemeSathi"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.scheme import Scheme, EligibilityRule


class CriterionStatus(str, Enum):
    MATCHED = "MATCHED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class CriterionResult(BaseModel):
    """Result of evaluating a single rule against a profile."""
    rule: EligibilityRule
    status: CriterionStatus
    user_value: Optional[str] = None
    detail: str = Field(..., description="Human-friendly explanation of why it matched, failed, or is unknown")


class EligibilityStatus(str, Enum):
    LIKELY_ELIGIBLE = "LIKELY ELIGIBLE"
    POSSIBLY_ELIGIBLE = "POSSIBLY ELIGIBLE"
    MORE_INFORMATION_NEEDED = "MORE INFORMATION NEEDED"
    NOT_ELIGIBLE = "NOT ELIGIBLE"


class SchemeEvaluationResult(BaseModel):
    """Overall evaluation output for a specific scheme against a citizen profile."""
    scheme: Scheme
    status: EligibilityStatus
    matched_criteria: List[CriterionResult] = Field(default_factory=list)
    failed_criteria: List[CriterionResult] = Field(default_factory=list)
    unknown_criteria: List[CriterionResult] = Field(default_factory=list)
    summary: str = Field(..., description="Short explanation of overall standing")
    missing_fields: List[str] = Field(default_factory=list, description="Fields required to resolve unknowns")

