"""Citizen Profile Pydantic Model for SchemeSathi"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CitizenProfile(BaseModel):
    """Structured citizen representation extracted from natural language.
    
    Fields that are not explicitly stated by the user remain None.
    AI must never invent missing information.
    """
    age: Optional[int] = Field(default=None, description="Age in completed years")
    state: Optional[str] = Field(default=None, description="Indian State or Union Territory")
    district: Optional[str] = Field(default=None, description="District within state")
    gender: Optional[str] = Field(default=None, description="Gender (female, male, transgender, other)")
    occupation: Optional[str] = Field(default=None, description="Primary occupation or profession")
    annual_income: Optional[float] = Field(default=None, description="Annual family income in INR")
    category: Optional[str] = Field(default=None, description="Social category: General, OBC, SC, ST, EWS")
    rural_or_urban: Optional[str] = Field(default=None, description="Area of residence: rural, urban, semi-urban")
    disability_status: Optional[bool] = Field(default=None, description="Whether person has a recognized disability")
    student_status: Optional[bool] = Field(default=None, description="Whether currently enrolled as a student")
    employment_status: Optional[str] = Field(default=None, description="Employment status: employed, unemployed, self-employed")
    farmer_status: Optional[bool] = Field(default=None, description="Whether person is an agricultural farmer")
    land_ownership: Optional[float] = Field(default=None, description="Agricultural land owned in hectares/acres")
    marital_status: Optional[str] = Field(default=None, description="Marital status: single, married, widowed, divorced")
    children_count: Optional[int] = Field(default=None, description="Number of dependent children")

    @field_validator("gender", mode="before")
    @classmethod
    def normalize_gender(cls, v):
        if not v or not isinstance(v, str):
            return None
        v_clean = v.strip().lower()
        if v_clean in ["female", "woman", "girl", "f"]:
            return "female"
        if v_clean in ["male", "man", "boy", "m"]:
            return "male"
        if v_clean in ["transgender", "trans"]:
            return "transgender"
        if v_clean in ["other", "non-binary"]:
            return "other"
        return v_clean

    @field_validator("state", mode="before")
    @classmethod
    def normalize_state(cls, v):
        if not v or not isinstance(v, str):
            return None
        # Title case standard Indian states
        cleaned = v.strip().title()
        if cleaned.lower() in ["punjab"]:
            return "Punjab"
        if cleaned.lower() in ["delhi", "nct of delhi", "new delhi"]:
            return "Delhi"
        if cleaned.lower() in ["haryana"]:
            return "Haryana"
        if cleaned.lower() in ["uttar pradesh", "up"]:
            return "Uttar Pradesh"
        if cleaned.lower() in ["maharashtra"]:
            return "Maharashtra"
        if cleaned.lower() in ["rajasthan"]:
            return "Rajasthan"
        if cleaned.lower() in ["tamil nadu", "tn"]:
            return "Tamil Nadu"
        if cleaned.lower() in ["karnataka"]:
            return "Karnataka"
        if cleaned.lower() in ["kerala"]:
            return "Kerala"
        if cleaned.lower() in ["west bengal", "wb"]:
            return "West Bengal"
        if cleaned.lower() in ["bihar"]:
            return "Bihar"
        if cleaned.lower() in ["gujarat"]:
            return "Gujarat"
        if cleaned.lower() in ["madhya pradesh", "mp"]:
            return "Madhya Pradesh"
        return cleaned

    @field_validator("rural_or_urban", mode="before")
    @classmethod
    def normalize_rural_urban(cls, v):
        if not v or not isinstance(v, str):
            return None
        v_clean = v.strip().lower()
        if "rural" in v_clean or "village" in v_clean:
            return "rural"
        if "urban" in v_clean or "city" in v_clean or "town" in v_clean:
            return "urban"
        return v_clean

    @field_validator("occupation", mode="before")
    @classmethod
    def normalize_occupation(cls, v):
        if not v or not isinstance(v, str):
            return None
        return v.strip().lower()

    @field_validator("age", mode="before")
    @classmethod
    def parse_age(cls, v):
        if v is None:
            return None
        try:
            val = int(v)
            if 0 <= val <= 130:
                return val
        except (ValueError, TypeError):
            pass
        return None

    @field_validator("annual_income", mode="before")
    @classmethod
    def parse_income(cls, v):
        if v is None:
            return None
        try:
            val = float(v)
            if val >= 0:
                return val
        except (ValueError, TypeError):
            pass
        return None

    def get_known_fields(self) -> dict:
        """Returns non-null fields with user-friendly representation."""
        return {k: v for k, v in self.model_dump().items() if v is not None}

    def get_missing_critical_fields(self) -> list[str]:
        """Identifies key eligibility fields currently unpopulated."""
        key_fields = ["age", "state", "occupation", "annual_income", "rural_or_urban"]
        return [f for f in key_fields if getattr(self, f) is None]

