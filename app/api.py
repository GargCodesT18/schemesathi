"""FastAPI Backend Server for SchemeSathi React Frontend"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from app.models.profile import CitizenProfile
from app.models.result import EligibilityStatus
from app.data.scheme_repository import SchemeRepository
from app.services.eligibility_service import EligibilityEngine
from app.services.explanation_service import ExplanationService
from app.services.export_service import ExportService
from app.services.llm_service import LLMService, OpenRouterProvider
from app.services.profile_service import ProfileService
from app.services.scheme_service import SchemeService

app = FastAPI(title="SchemeSathi API", version="0.2.0")

# Enable CORS for React frontend (Vite dev server or static build)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
repo = SchemeRepository()
engine = EligibilityEngine()
explanation = ExplanationService()
scheme_service = SchemeService(repository=repo, engine=engine, explanation_service=explanation)


class EvaluateRequest(BaseModel):
    text: Optional[str] = ""
    profile: Optional[Dict[str, Any]] = None
    category: Optional[str] = "All"
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    merge: Optional[bool] = False


class ExportRequest(BaseModel):
    profile: Optional[Dict[str, Any]] = None
    category: Optional[str] = "All"


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "SchemeSathi", "version": "0.2.0"}


@app.get("/api/schemes")
def get_schemes(category: Optional[str] = None):
    schemes = repo.get_all()
    if category and category.lower() != "all":
        schemes = [s for s in schemes if s.category.lower() == category.lower()]
    return {
        "categories": ["All"] + repo.get_all_categories(),
        "schemes": [s.model_dump() for s in schemes],
        "total": len(schemes)
    }


@app.post("/api/evaluate")
def evaluate_citizen(req: EvaluateRequest):
    # 1. Profile Extraction or Hydration
    base_profile = None
    if req.profile:
        try:
            base_profile = CitizenProfile(**{k: v for k, v in req.profile.items() if v is not None})
        except Exception:
            base_profile = None

    profile = base_profile or CitizenProfile()
    extraction_error = None

    # If text is provided, extract via LLMService
    if req.text and req.text.strip():
        try:
            provider = OpenRouterProvider(
                api_key=req.api_key.strip() if req.api_key else None,
                model=req.model_name.strip() if req.model_name else None
            )
            llm_service = LLMService(provider=provider)
            profile_service = ProfileService(llm_service=llm_service)

            if req.merge and base_profile and base_profile.get_known_fields():
                profile = profile_service.merge_profiles(base_profile, req.text.strip())
            else:
                profile = profile_service.create_from_text(req.text.strip())
        except Exception as err:
            extraction_error = str(err)
            if not base_profile:
                profile = CitizenProfile()

    # 2. Evaluate Schemes
    results = scheme_service.evaluate_citizen(profile, category_filter=req.category)

    # 3. Format Output
    formatted_results = [explanation.format_evaluation_details(r) for r in results]
    missing_prompt = scheme_service.get_missing_info_question(profile, results)

    # Count statistics
    likely_count = sum(1 for r in results if r.status == EligibilityStatus.LIKELY_ELIGIBLE)
    possibly_count = sum(1 for r in results if r.status == EligibilityStatus.POSSIBLY_ELIGIBLE)
    more_info_count = sum(1 for r in results if r.status == EligibilityStatus.MORE_INFORMATION_NEEDED)
    not_eligible_count = sum(1 for r in results if r.status == EligibilityStatus.NOT_ELIGIBLE)

    return {
        "profile": profile.model_dump(),
        "known_fields": profile.get_known_fields(),
        "results": formatted_results,
        "metrics": {
            "likely": likely_count,
            "possibly": possibly_count,
            "more_info": more_info_count,
            "not_eligible": not_eligible_count,
            "total": len(results)
        },
        "missing_prompt": missing_prompt,
        "extraction_error": extraction_error
    }


@app.post("/api/export/pdf")
def export_pdf(req: ExportRequest):
    profile = CitizenProfile(**(req.profile or {}))
    results = scheme_service.evaluate_citizen(profile, category_filter=req.category)
    pdf_bytes = ExportService.generate_csc_checklist_pdf(profile, results)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=SchemeSathi_CSC_Checklist.pdf"}
    )


@app.post("/api/export/text")
def export_text(req: ExportRequest):
    profile = CitizenProfile(**(req.profile or {}))
    results = scheme_service.evaluate_citizen(profile, category_filter=req.category)
    txt = ExportService.generate_csc_checklist_text(profile, results)
    return Response(
        content=txt,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=SchemeSathi_Verification_Docket.txt"}
    )


# Mount static React build if it exists
frontend_dist = ROOT_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")

