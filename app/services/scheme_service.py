"""Scheme Navigator Orchestrator Service"""
from typing import List, Optional
from app.data.scheme_repository import SchemeRepository
from app.models.profile import CitizenProfile
from app.models.result import SchemeEvaluationResult
from app.services.eligibility_service import EligibilityEngine
from app.services.explanation_service import ExplanationService


class SchemeService:
    """High-level service coordinating scheme discovery, eligibility evaluation, and explanations."""

    def __init__(
        self,
        repository: Optional[SchemeRepository] = None,
        engine: Optional[EligibilityEngine] = None,
        explanation_service: Optional[ExplanationService] = None,
    ):
        self.repository = repository or SchemeRepository()
        self.engine = engine or EligibilityEngine()
        self.explanation = explanation_service or ExplanationService()

    def evaluate_citizen(
        self,
        profile: CitizenProfile,
        category_filter: Optional[str] = None
    ) -> List[SchemeEvaluationResult]:
        """Evaluates all registered schemes (or filtered by category) against the citizen's profile."""
        schemes = self.repository.get_all()
        if category_filter and category_filter.lower() != "all":
            schemes = [s for s in schemes if s.category.lower() == category_filter.lower()]
        
        return self.engine.evaluate_all(schemes, profile)

    def get_missing_info_question(
        self,
        profile: CitizenProfile,
        results: List[SchemeEvaluationResult]
    ) -> Optional[str]:
        """Generates an intelligent follow-up question to clarify unfulfilled eligibility criteria."""
        return self.explanation.generate_missing_info_prompt(profile, results)

