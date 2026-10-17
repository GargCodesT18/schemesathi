"""Unit tests for deterministic EligibilityEngine and rule evaluation"""
import pytest
from app.models.profile import CitizenProfile
from app.models.scheme import Scheme, EligibilityRule
from app.models.result import EligibilityStatus, CriterionStatus
from app.services.eligibility_service import EligibilityEngine


@pytest.fixture
def engine():
    return EligibilityEngine()


@pytest.fixture
def sample_farmer_scheme():
    return Scheme(
        id="test-kisan",
        name="Test Kisan Scheme",
        description="Support for farmers",
        category="Agriculture",
        benefits="₹6,000 per year",
        eligibility_rules=[
            EligibilityRule(field="occupation", operator="equals", value="farmer", description="Must be a farmer"),
            EligibilityRule(field="age", operator="greater_than_or_equal", value=18, description="Age >= 18"),
            EligibilityRule(field="annual_income", operator="less_than_or_equal", value=300000, description="Income <= 3L")
        ],
        required_documents=["Aadhaar", "Land Records"],
        application_information="Apply online",
        state_scope=["All-India"],
        source_name="Gov Authority",
        source_url="https://example.gov.in",
        last_verified="2026-01-01"
    )


def test_rule_comparison_operators(engine):
    # equals
    assert engine._compare("farmer", "equals", "farmer")
    assert engine._compare("Farmer", "equals", "farmer")
    assert not engine._compare("doctor", "equals", "farmer")

    # greater_than_or_equal
    assert engine._compare(42, "greater_than_or_equal", 18)
    assert engine._compare(18, "greater_than_or_equal", 18)
    assert not engine._compare(17, "greater_than_or_equal", 18)

    # less_than_or_equal
    assert engine._compare(200000, "less_than_or_equal", 300000)
    assert not engine._compare(400000, "less_than_or_equal", 300000)

    # in
    assert engine._compare("vendor", "in", ["vendor", "hawker"])
    assert not engine._compare("engineer", "in", ["vendor", "hawker"])


def test_scheme_fully_eligible(engine, sample_farmer_scheme):
    profile = CitizenProfile(
        occupation="farmer",
        age=42,
        annual_income=200000
    )
    result = engine.evaluate_scheme(sample_farmer_scheme, profile)
    assert result.status == EligibilityStatus.LIKELY_ELIGIBLE
    assert len(result.matched_criteria) == 3
    assert len(result.failed_criteria) == 0
    assert len(result.unknown_criteria) == 0


def test_scheme_ineligible_due_to_failed_rule(engine, sample_farmer_scheme):
    profile = CitizenProfile(
        occupation="engineer",  # Does not match farmer
        age=42,
        annual_income=200000
    )
    result = engine.evaluate_scheme(sample_farmer_scheme, profile)
    assert result.status == EligibilityStatus.NOT_ELIGIBLE
    assert len(result.failed_criteria) == 1
    assert result.failed_criteria[0].rule.field == "occupation"


def test_scheme_possibly_eligible_with_unknown_fields(engine, sample_farmer_scheme):
    profile = CitizenProfile(
        occupation="farmer",
        age=42
        # annual_income is missing (None)
    )
    result = engine.evaluate_scheme(sample_farmer_scheme, profile)
    assert result.status == EligibilityStatus.POSSIBLY_ELIGIBLE
    assert len(result.matched_criteria) == 2
    assert len(result.unknown_criteria) == 1
    assert "annual_income" in result.missing_fields


def test_scheme_more_info_needed_when_all_unknown(engine, sample_farmer_scheme):
    profile = CitizenProfile()  # Nothing known
    result = engine.evaluate_scheme(sample_farmer_scheme, profile)
    assert result.status == EligibilityStatus.MORE_INFORMATION_NEEDED
    assert len(result.unknown_criteria) == 3


def test_state_scoped_scheme(engine):
    punjab_scheme = Scheme(
        id="pb-scheme",
        name="Punjab Scheme",
        description="For Punjab residents only",
        category="Agriculture",
        benefits="Subsidy",
        eligibility_rules=[
            EligibilityRule(field="occupation", operator="equals", value="farmer")
        ],
        required_documents=[],
        application_information="Apply locally",
        state_scope=["Punjab"],
        source_name="Gov Punjab",
        source_url="https://pb.gov.in",
        last_verified="2026-01-01"
    )
    
    # Resident of Haryana should fail
    haryana_citizen = CitizenProfile(occupation="farmer", state="Haryana")
    res_haryana = engine.evaluate_scheme(punjab_scheme, haryana_citizen)
    assert res_haryana.status == EligibilityStatus.NOT_ELIGIBLE

    # Resident of Punjab should be likely eligible
    punjab_citizen = CitizenProfile(occupation="farmer", state="Punjab")
    res_punjab = engine.evaluate_scheme(punjab_scheme, punjab_citizen)
    assert res_punjab.status == EligibilityStatus.LIKELY_ELIGIBLE

