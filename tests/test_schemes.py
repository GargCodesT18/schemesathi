"""Unit tests for SchemeRepository and schemes dataset integrity"""
import pytest
from app.data.scheme_repository import SchemeRepository


@pytest.fixture
def repo():
    return SchemeRepository()


def test_schemes_load_successfully(repo):
    schemes = repo.get_all()
    assert len(schemes) >= 10, f"Expected at least 10 curated schemes, got {len(schemes)}"


def test_schemes_have_valid_provenance(repo):
    schemes = repo.get_all()
    for s in schemes:
        assert s.id, "Scheme must have an id"
        assert s.name, "Scheme must have a title"
        assert s.category, "Scheme must belong to a category"
        assert s.source_name, f"Scheme {s.id} missing source_name"
        assert s.source_url.startswith("http"), f"Scheme {s.id} missing valid source_url"
        assert s.last_verified, f"Scheme {s.id} missing last_verified timestamp"
        assert len(s.eligibility_rules) > 0, f"Scheme {s.id} has no eligibility rules"


def test_scheme_lookup_by_id(repo):
    pm_kisan = repo.get_by_id("pm-kisan")
    assert pm_kisan is not None
    assert pm_kisan.short_name == "PM-KISAN"
    assert pm_kisan.category == "Agriculture"

    non_existent = repo.get_by_id("non-existent-scheme-id")
    assert non_existent is None


def test_scheme_categories(repo):
    categories = repo.get_all_categories()
    assert "Agriculture" in categories
    assert "Housing" in categories
    assert "Senior Citizens" in categories
    assert "Women" in categories
    assert "Education" in categories

    agri_schemes = repo.get_by_category("Agriculture")
    assert len(agri_schemes) >= 2
    for s in agri_schemes:
        assert s.category == "Agriculture"

