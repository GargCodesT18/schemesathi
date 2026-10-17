"""Profile Service for profile lifecycle, merging, and validation"""
from typing import Dict, Any, Optional
from app.models.profile import CitizenProfile
from app.services.llm_service import LLMService


class ProfileService:
    """Manages profile extraction, incremental updates, and validation."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()

    def create_from_text(self, text: str) -> CitizenProfile:
        """Extracts and validates a fresh CitizenProfile from raw natural language input."""
        extracted_dict = self.llm_service.extract_profile(text)
        return CitizenProfile(**extracted_dict)

    def merge_profiles(self, existing: CitizenProfile, new_text: str) -> CitizenProfile:
        """Merges new citizen disclosures into an existing profile without losing known data."""
        new_dict = self.llm_service.extract_profile(new_text)
        
        merged_data = existing.model_dump()
        for k, v in new_dict.items():
            if v is not None and k in merged_data:
                merged_data[k] = v

        # Demographic sanity reconciliation:
        # If age is senior (>= 60), clear stale student/youth statuses unless explicitly asserted
        if merged_data.get("age") is not None and merged_data["age"] >= 60:
            if new_dict.get("student_status") is not True:
                merged_data["student_status"] = False
                if merged_data.get("occupation") == "student":
                    merged_data["occupation"] = new_dict.get("occupation") or "senior citizen"

        return CitizenProfile(**merged_data)

    def update_field_manually(self, profile: CitizenProfile, field: str, value: Any) -> CitizenProfile:
        """Allows direct user refinement of profile fields in the UI."""
        data = profile.model_dump()
        if field in data:
            data[field] = value
        return CitizenProfile(**data)

