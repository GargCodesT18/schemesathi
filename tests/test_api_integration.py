"""Integration test verifying models and their connection to the frontend API"""
import pytest
from fastapi.testclient import TestClient
from app.api import app
from app.models.profile import CitizenProfile
from app.models.scheme import Scheme, EligibilityRule
from app.models.result import EligibilityStatus, CriterionStatus, SchemeEvaluationResult

client = TestClient(app)


def test_models_direct_integrity():
    """Verify all Pydantic models in app/models behave according to specification."""
    # Profile validation & normalizations
    p = CitizenProfile(
        age="42",
        state="punjab",
        occupation="FARMER",
        annual_income="200000",
        rural_or_urban="in a rural area",
        farmer_status=True
    )
    assert p.age == 42
    assert p.state == "Punjab"
    assert p.occupation == "farmer"
    assert p.annual_income == 200000.0
    assert p.rural_or_urban == "rural"
    assert p.farmer_status is True

    # Scheme and EligibilityRule models
    rule = EligibilityRule(
        field="occupation",
        operator="equals",
        value="farmer",
        description="Must be a cultivator"
    )
    assert rule.field == "occupation"

    scheme = Scheme(
        id="test-id",
        name="Test Scheme Title",
        description="Scheme description",
        category="Agriculture",
        benefits="Rs 6000",
        eligibility_rules=[rule],
        required_documents=["Aadhaar"],
        application_information="Apply at CSC",
        state_scope=["Punjab"],
        source_name="Gov Authority",
        source_url="https://gov.in",
        last_verified="2026-03-01"
    )
    assert scheme.id == "test-id"
    assert len(scheme.eligibility_rules) == 1


def test_frontend_api_schemes_endpoint():
    """Verify GET /api/schemes returns categories and scheme objects expected by React UI."""
    response = client.get("/api/schemes")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "schemes" in data
    assert "All" in data["categories"]
    assert "Agriculture" in data["categories"]
    assert len(data["schemes"]) >= 10


def test_frontend_api_evaluate_endpoint():
    """Verify POST /api/evaluate handles payload exactly as sent by React App.jsx."""
    payload = {
        "text": "",
        "profile": {
            "age": 42,
            "state": "Punjab",
            "occupation": "farmer",
            "annual_income": 200000,
            "farmer_status": True,
            "rural_or_urban": "rural"
        },
        "category": "All"
    }
    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Ensure all keys expected by frontend exist
    assert "profile" in data
    assert "known_fields" in data
    assert "results" in data
    assert "metrics" in data

    # Check metrics structure
    metrics = data["metrics"]
    assert "likely" in metrics
    assert "possibly" in metrics
    assert "more_info" in metrics
    assert "not_eligible" in metrics
    assert metrics["likely"] >= 1  # PM-KISAN should be Likely Eligible

    # Check individual result card structure
    first_res = data["results"][0]
    expected_card_keys = [
        "scheme_name", "short_name", "status", "category",
        "benefits", "summary", "matched", "failed", "unknown",
        "source_name", "source_url", "required_documents", "application_info"
    ]
    for key in expected_card_keys:
        assert key in first_res, f"Missing {key} in result returned to frontend"


def test_frontend_api_export_pdf_endpoint():
    """Verify POST /api/export/pdf returns a valid downloadable PDF for CSC Kendra visit."""
    payload = {
        "profile": {
            "age": 42,
            "state": "Punjab",
            "occupation": "farmer",
            "annual_income": 200000,
            "farmer_status": True
        },
        "category": "All"
    }
    response = client.post("/api/export/pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 500


def test_frontend_api_export_text_endpoint():
    """Verify POST /api/export/text returns a valid formatted text docket."""
    payload = {
        "profile": {
            "age": 42,
            "state": "Punjab",
            "occupation": "farmer"
        },
        "category": "All"
    }
    response = client.post("/api/export/text", json=payload)
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    text = response.text
    assert "SCHEMESATHI" in text
    assert "[ ]" in text

