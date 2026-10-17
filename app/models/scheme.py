"""Scheme and Eligibility Rule Pydantic Models for SchemeSathi"""
from typing import Any, List, Optional, Union
from pydantic import BaseModel, Field


class EligibilityRule(BaseModel):
    """Deterministic eligibility rule representation."""
    field: str = Field(..., description="Target profile field name")
    operator: str = Field(
        ...,
        description="Comparison operator: equals, not_equals, greater_than, greater_than_or_equal, less_than, less_than_or_equal, in, not_in"
    )
    value: Any = Field(..., description="Expected value or boundary")
    description: Optional[str] = Field(None, description="Citizen-readable explanation of this requirement")


class Scheme(BaseModel):
    """Government Scheme representation with verifiable source provenance."""
    id: str = Field(..., description="Unique scheme identifier")
    name: str = Field(..., description="Full official title of scheme")
    short_name: Optional[str] = Field(None, description="Common acronym or colloquial name")
    description: str = Field(..., description="Overview of scheme intent and scope")
    category: str = Field(..., description="Sector category (e.g. Agriculture, Education, Women)")
    benefits: str = Field(..., description="Summary of financial or in-kind support provided")
    eligibility_rules: List[EligibilityRule] = Field(default_factory=list, description="Rules to satisfy")
    required_documents: List[str] = Field(default_factory=list, description="Mandatory application papers")
    application_information: str = Field(..., description="How and where to apply")
    state_scope: List[str] = Field(default_factory=lambda: ["All-India"], description="Applicable Indian states")
    source_name: str = Field(..., description="Official government authority or portal name")
    source_url: str = Field(..., description="Direct official portal URL")
    last_verified: str = Field(..., description="Date of verification (YYYY-MM-DD)")

