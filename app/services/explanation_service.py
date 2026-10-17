"""Explanation Service for transparent criterion-by-criterion citizen feedback"""
from typing import List, Optional
from app.models.profile import CitizenProfile
from app.models.result import (
    CriterionStatus,
    EligibilityStatus,
    SchemeEvaluationResult,
)


class ExplanationService:
    """Transforms raw evaluation results into clear, structured, transparent citizen guidance."""

    @staticmethod
    def get_criterion_icon(status: CriterionStatus) -> str:
        if status == CriterionStatus.MATCHED:
            return "✓"
        elif status == CriterionStatus.FAILED:
            return "✗"
        return "?"

    @classmethod
    def format_evaluation_details(cls, result: SchemeEvaluationResult) -> dict:
        """Generates structured breakdown for UI cards and reports."""
        matched_items = [
            f"✓ {c.detail}" for c in result.matched_criteria
        ]
        failed_items = [
            f"✗ {c.detail}" for c in result.failed_criteria
        ]
        unknown_items = [
            f"? {c.detail}" for c in result.unknown_criteria
        ]

        return {
            "scheme_name": result.scheme.name,
            "short_name": result.scheme.short_name or result.scheme.name,
            "status": result.status.value,
            "category": result.scheme.category,
            "benefits": result.scheme.benefits,
            "summary": result.summary,
            "matched": matched_items,
            "failed": failed_items,
            "unknown": unknown_items,
            "source_name": result.scheme.source_name,
            "source_url": result.scheme.source_url,
            "required_documents": result.scheme.required_documents,
            "application_info": result.scheme.application_information,
        }

    @staticmethod
    def generate_missing_info_prompt(profile: CitizenProfile, top_results: List[SchemeEvaluationResult]) -> Optional[str]:
        """Identifies the most impactful missing information and crafts a single focused clarifying question."""
        missing_fields_frequency = {}
        for res in top_results:
            if res.status in (EligibilityStatus.POSSIBLY_ELIGIBLE, EligibilityStatus.MORE_INFORMATION_NEEDED):
                for f in res.missing_fields:
                    missing_fields_frequency[f] = missing_fields_frequency.get(f, 0) + 1

        if not missing_fields_frequency:
            return None

        # Sort fields by frequency of blocking schemes
        sorted_fields = sorted(missing_fields_frequency.items(), key=lambda x: -x[1])
        top_missing = [f[0] for f in sorted_fields[:2]]  # At most 2 fields

        field_labels = {
            "annual_income": "approximate annual family income",
            "age": "age",
            "state": "state of residence",
            "rural_or_urban": "whether you reside in a rural or urban area",
            "land_ownership": "agricultural land ownership (in acres)",
            "student_status": "whether you are currently enrolled as a student",
            "gender": "gender",
            "employment_status": "employment status",
        }

        readable_terms = [field_labels.get(f, f.replace("_", " ")) for f in top_missing]
        if len(readable_terms) == 1:
            return f"To confirm your eligibility for more schemes, could you share your {readable_terms[0]}?"
        else:
            return f"To confirm your eligibility for more schemes, could you share your {readable_terms[0]} and {readable_terms[1]}?"

    @staticmethod
    def get_legal_disclaimer() -> str:
        return (
            "Notice: SchemeSathi provides educational navigation based on published government criteria. "
            "It does not guarantee scheme approval. Final eligibility and disbursement are determined "
            "solely by the respective government authority upon official document verification."
        )

