"""Deterministic Eligibility Engine for SchemeSathi"""
from typing import Any, List, Optional
from app.models.profile import CitizenProfile
from app.models.scheme import Scheme, EligibilityRule
from app.models.result import (
    CriterionStatus,
    CriterionResult,
    EligibilityStatus,
    SchemeEvaluationResult,
)


class EligibilityEngine:
    """Evaluates CitizenProfile against Scheme eligibility criteria using deterministic Python rules.
    
    The LLM never decides eligibility. This engine provides complete transparency and auditability.
    """

    @staticmethod
    def _compare(user_val: Any, operator: str, rule_val: Any) -> bool:
        """Compares user value against rule condition with robust type coercion."""
        if operator == "equals":
            if isinstance(user_val, str) and isinstance(rule_val, str):
                return user_val.strip().lower() == rule_val.strip().lower()
            return user_val == rule_val

        elif operator == "not_equals":
            if isinstance(user_val, str) and isinstance(rule_val, str):
                return user_val.strip().lower() != rule_val.strip().lower()
            return user_val != rule_val

        elif operator == "greater_than":
            return float(user_val) > float(rule_val)

        elif operator == "greater_than_or_equal":
            return float(user_val) >= float(rule_val)

        elif operator == "less_than":
            return float(user_val) < float(rule_val)

        elif operator == "less_than_or_equal":
            return float(user_val) <= float(rule_val)

        elif operator == "in":
            if isinstance(rule_val, list):
                if isinstance(user_val, str):
                    return any(user_val.strip().lower() == str(item).strip().lower() for item in rule_val)
                return user_val in rule_val
            elif isinstance(rule_val, str) and isinstance(user_val, str):
                return user_val.strip().lower() in rule_val.strip().lower()
            return False

        elif operator == "not_in":
            if isinstance(rule_val, list):
                if isinstance(user_val, str):
                    return not any(user_val.strip().lower() == str(item).strip().lower() for item in rule_val)
                return user_val not in rule_val
            return True

        else:
            raise ValueError(f"Unsupported rule operator: {operator}")

    def evaluate_rule(self, rule: EligibilityRule, profile: CitizenProfile) -> CriterionResult:
        """Evaluates an individual rule against a citizen's profile."""
        field_name = rule.field
        user_val = getattr(profile, field_name, None)

        rule_desc = rule.description or f"{field_name} {rule.operator} {rule.value}"

        if user_val is None:
            return CriterionResult(
                rule=rule,
                status=CriterionStatus.UNKNOWN,
                user_value=None,
                detail=f"{rule_desc} (Citizen has not provided {field_name})"
            )

        try:
            passed = self._compare(user_val, rule.operator, rule.value)
            if passed:
                return CriterionResult(
                    rule=rule,
                    status=CriterionStatus.MATCHED,
                    user_value=str(user_val),
                    detail=f"{rule_desc} (Citizen value: {user_val})"
                )
            else:
                return CriterionResult(
                    rule=rule,
                    status=CriterionStatus.FAILED,
                    user_value=str(user_val),
                    detail=f"{rule_desc} (Citizen value: {user_val} does not satisfy requirement)"
                )
        except (ValueError, TypeError) as err:
            return CriterionResult(
                rule=rule,
                status=CriterionStatus.UNKNOWN,
                user_value=str(user_val),
                detail=f"Unable to compare {field_name} due to format mismatch: {err}"
            )

    def evaluate_scheme(self, scheme: Scheme, profile: CitizenProfile) -> SchemeEvaluationResult:
        """Evaluates all rules for a scheme and produces an overall transparent assessment."""
        matched: List[CriterionResult] = []
        failed: List[CriterionResult] = []
        unknown: List[CriterionResult] = []
        missing_fields: List[str] = []

        # Check state scope if scheme is state-specific
        if scheme.state_scope and "All-India" not in scheme.state_scope:
            state_val = profile.state
            state_rule = EligibilityRule(
                field="state",
                operator="in",
                value=scheme.state_scope,
                description=f"Must reside in one of: {', '.join(scheme.state_scope)}"
            )
            state_result = self.evaluate_rule(state_rule, profile)
            if state_result.status == CriterionStatus.MATCHED:
                matched.append(state_result)
            elif state_result.status == CriterionStatus.FAILED:
                failed.append(state_result)
            else:
                unknown.append(state_result)
                missing_fields.append("state")

        for rule in scheme.eligibility_rules:
            res = self.evaluate_rule(rule, profile)
            if res.status == CriterionStatus.MATCHED:
                matched.append(res)
            elif res.status == CriterionStatus.FAILED:
                failed.append(res)
            else:
                unknown.append(res)
                if rule.field not in missing_fields:
                    missing_fields.append(rule.field)

        # Determine overall status
        if failed:
            status = EligibilityStatus.NOT_ELIGIBLE
            summary = f"Not eligible: {len(failed)} criterion did not match."
        elif not matched and unknown:
            status = EligibilityStatus.MORE_INFORMATION_NEEDED
            summary = "More information needed to determine eligibility."
        elif matched and unknown:
            status = EligibilityStatus.POSSIBLY_ELIGIBLE
            summary = f"Possibly eligible: {len(matched)} criteria matched, {len(unknown)} pending additional details."
        elif matched and not unknown and not failed:
            status = EligibilityStatus.LIKELY_ELIGIBLE
            summary = f"Likely eligible: All {len(matched)} evaluated criteria satisfied."
        else:
            status = EligibilityStatus.MORE_INFORMATION_NEEDED
            summary = "No criteria could be evaluated from current profile."

        return SchemeEvaluationResult(
            scheme=scheme,
            status=status,
            matched_criteria=matched,
            failed_criteria=failed,
            unknown_criteria=unknown,
            summary=summary,
            missing_fields=missing_fields
        )

    def evaluate_all(self, schemes: List[Scheme], profile: CitizenProfile) -> List[SchemeEvaluationResult]:
        """Evaluates multiple schemes and orders them logically (Likely -> Possibly -> More Info -> Not Eligible)."""
        results = [self.evaluate_scheme(s, profile) for s in schemes]
        
        status_priority = {
            EligibilityStatus.LIKELY_ELIGIBLE: 0,
            EligibilityStatus.POSSIBLY_ELIGIBLE: 1,
            EligibilityStatus.MORE_INFORMATION_NEEDED: 2,
            EligibilityStatus.NOT_ELIGIBLE: 3,
        }
        
        # Sort by status priority, then by number of matched criteria descending
        results.sort(key=lambda r: (status_priority[r.status], -len(r.matched_criteria)))
        return results

