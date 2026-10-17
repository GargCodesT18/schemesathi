"""Unit tests for CitizenProfile Pydantic model and normalizations"""
import pytest
from app.models.profile import CitizenProfile


def test_profile_empty_defaults():
    profile = CitizenProfile()
    assert profile.age is None
    assert profile.state is None
    assert profile.occupation is None
    assert profile.annual_income is None
    assert len(profile.get_known_fields()) == 0
    assert len(profile.get_missing_critical_fields()) == 5


def test_profile_valid_assignment():
    profile = CitizenProfile(
        age=42,
        state="Punjab",
        occupation="farmer",
        annual_income=200000,
        farmer_status=True
    )
    assert profile.age == 42
    assert profile.state == "Punjab"
    assert profile.occupation == "farmer"
    assert profile.annual_income == 200000.0
    assert profile.farmer_status is True


def test_profile_gender_normalization():
    p1 = CitizenProfile(gender="Female")
    assert p1.gender == "female"
    p2 = CitizenProfile(gender="woman")
    assert p2.gender == "female"
    p3 = CitizenProfile(gender="man")
    assert p3.gender == "male"
    p4 = CitizenProfile(gender="Transgender")
    assert p4.gender == "transgender"


def test_profile_state_normalization():
    p1 = CitizenProfile(state="punjab")
    assert p1.state == "Punjab"
    p2 = CitizenProfile(state="up")
    assert p2.state == "Uttar Pradesh"
    p3 = CitizenProfile(state="new delhi")
    assert p3.state == "Delhi"


def test_profile_rural_urban_normalization():
    p1 = CitizenProfile(rural_or_urban="in a rural village")
    assert p1.rural_or_urban == "rural"
    p2 = CitizenProfile(rural_or_urban="metro city")
    assert p2.rural_or_urban == "urban"


def test_profile_invalid_age_and_income_handling():
    p = CitizenProfile(age="invalid", annual_income="unknown")
    assert p.age is None
    assert p.annual_income is None

    p_negative = CitizenProfile(age=-5, annual_income=-100)
    assert p_negative.age is None
    assert p_negative.annual_income is None

