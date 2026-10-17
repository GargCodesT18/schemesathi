"""Unit tests for ExportService (CSC PDF and Text Docket generation)"""
import pytest
from app.models.profile import CitizenProfile
from app.models.scheme import Scheme, EligibilityRule
from app.services.eligibility_service import EligibilityEngine
from app.services.export_service import ExportService


@pytest.fixture
def sample_data():
    profile = CitizenProfile(
        age=42,
        state="Punjab",
        occupation="farmer",
        annual_income=200000,
        farmer_status=True
    )
    scheme = Scheme(
        id="test-pm-kisan",
        name="Pradhan Mantri Kisan Samman Nidhi",
        short_name="PM-KISAN",
        description="Direct income support to farmers",
        category="Agriculture",
        benefits="Rs 6,000 per year",
        eligibility_rules=[
            EligibilityRule(field="occupation", operator="equals", value="farmer", description="Cultivator")
        ],
        required_documents=["Aadhaar Card", "Land Records (Khasra)"],
        application_information="Apply online at pmkisan.gov.in",
        state_scope=["All-India"],
        source_name="Ministry of Agriculture",
        source_url="https://pmkisan.gov.in",
        last_verified="2026-03-01"
    )
    engine = EligibilityEngine()
    results = [engine.evaluate_scheme(scheme, profile)]
    return profile, results


def test_generate_csc_checklist_pdf(sample_data):
    profile, results = sample_data
    pdf_bytes = ExportService.generate_csc_checklist_pdf(profile, results)
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    # Standard PDF file header
    assert pdf_bytes.startswith(b"%PDF")


def test_generate_csc_checklist_text(sample_data):
    profile, results = sample_data
    text = ExportService.generate_csc_checklist_text(profile, results)
    
    assert "SCHEMESATHI" in text
    assert "Punjab" in text
    assert "PM-KISAN" in text
    assert "[ ] Aadhaar Card" in text
    assert "[ ] Land Records (Khasra)" in text
    assert "https://pmkisan.gov.in" in text

