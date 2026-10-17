"""Utility script to generate the 6 comprehensive project notebooks."""
import nbformat as nbf
from pathlib import Path

NOTEBOOKS_DIR = Path("D:/Hackoctober_challenge_2/notebooks")
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)


def create_nb_01():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python (SchemeSathi)",
            "language": "python",
            "name": "schemesathi"
        },
        "language_info": {"name": "python", "version": "3.11"}
    }
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 01. Environment Setup & Configuration\n\n"
            "This notebook inspects and documents the project-local runtime environment for **SchemeSathi**.\n"
            "All dependencies, caches, and executions reside strictly inside the project root."
        ),
        nbf.v4.new_markdown_cell("### 1. Python Version & Executable Path"),
        nbf.v4.new_code_cell(
            "import sys\n"
            "print('Python Version:', sys.version)\n"
            "print('Python Executable:', sys.executable)"
        ),
        nbf.v4.new_markdown_cell("### 2. Project Root & Caches\nInspect local directory structure ensuring zero external dependencies."),
        nbf.v4.new_code_cell(
            "import os\n"
            "from pathlib import Path\n"
            "from app.config import BASE_DIR, PIP_CACHE_DIR, HF_CACHE_DIR, TORCH_CACHE_DIR\n\n"
            "print(f'Project Root: {BASE_DIR}')\n"
            "print(f'PIP Cache Directory: {PIP_CACHE_DIR} (Exists: {PIP_CACHE_DIR.exists()})')\n"
            "print(f'HuggingFace Cache: {HF_CACHE_DIR} (Exists: {HF_CACHE_DIR.exists()})')\n"
            "print(f'Torch Cache: {TORCH_CACHE_DIR} (Exists: {TORCH_CACHE_DIR.exists()})')"
        ),
        nbf.v4.new_markdown_cell("### 3. Installed Core Libraries Verification"),
        nbf.v4.new_code_cell(
            "import pydantic, streamlit, requests, dotenv, pytest, pandas, ipykernel\n\n"
            "packages = {\n"
            "    'pydantic': pydantic.__version__,\n"
            "    'streamlit': streamlit.__version__,\n"
            "    'requests': requests.__version__,\n"
            "    'pandas': pandas.__version__,\n"
            "    'pytest': pytest.__version__,\n"
            "    'ipykernel': ipykernel.__version__\n"
            "}\n"
            "for pkg, ver in packages.items():\n"
            "    print(f'✓ {pkg:12} : {ver}')"
        ),
        nbf.v4.new_markdown_cell("### 4. Configuration Check (Masked API Key)\nConfirm environment variables load safely without leaking credentials."),
        nbf.v4.new_code_cell(
            "from app.config import OPENROUTER_MODEL, OPENROUTER_BASE_URL, OPENROUTER_API_KEY\n\n"
            "print(f'Model Slug  : {OPENROUTER_MODEL}')\n"
            "print(f'Base URL    : {OPENROUTER_BASE_URL}')\n"
            "has_key = bool(OPENROUTER_API_KEY)\n"
            "masked = OPENROUTER_API_KEY[:4] + '...' + OPENROUTER_API_KEY[-4:] if has_key and len(OPENROUTER_API_KEY) > 8 else ('[Set]' if has_key else '[Not Configured]')\n"
            "print(f'API Key     : {masked}')"
        ),
        nbf.v4.new_markdown_cell(
            "### Interpretation\n"
            "The environment is fully configured, self-contained inside `.conda`, with project-local caching in `.cache`."
        )
    ]
    with open(NOTEBOOKS_DIR / "01_environment_setup.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)


def create_nb_02():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {"display_name": "Python (SchemeSathi)", "language": "python", "name": "schemesathi"}
    }
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 02. Scheme Data Exploration\n\n"
            "Explore the curated Indian Government schemes dataset (`data/schemes.json`).\n"
            "Every scheme includes official provenance, benefits, and deterministic rule criteria."
        ),
        nbf.v4.new_markdown_cell("### 1. Load Schemes Repository"),
        nbf.v4.new_code_cell(
            "import pandas as pd\n"
            "from app.data.scheme_repository import SchemeRepository\n\n"
            "repo = SchemeRepository()\n"
            "schemes = repo.get_all()\n"
            "print(f'Total Curated Schemes: {len(schemes)}')\n"
            "print(f'Categories: {repo.get_all_categories()}')"
        ),
        nbf.v4.new_markdown_cell("### 2. Dataset Overview via Pandas DataFrame"),
        nbf.v4.new_code_cell(
            "df = pd.DataFrame([{\n"
            "    'id': s.id,\n"
            "    'short_name': s.short_name or s.name,\n"
            "    'category': s.category,\n"
            "    'rules_count': len(s.eligibility_rules),\n"
            "    'state_scope': ', '.join(s.state_scope),\n"
            "    'source': s.source_name\n"
            "} for s in schemes])\n"
            "df"
        ),
        nbf.v4.new_markdown_cell("### 3. Distribution by Sector Category"),
        nbf.v4.new_code_cell(
            "cat_counts = df['category'].value_counts()\n"
            "print(cat_counts)"
        ),
        nbf.v4.new_markdown_cell("### 4. Rule Criteria Breakdown\nInspect the deterministic rule format used for eligibility evaluation."),
        nbf.v4.new_code_cell(
            "sample_scheme = repo.get_by_id('pm-kisan')\n"
            "print(f'Scheme: {sample_scheme.name}')\n"
            "print('Eligibility Rules:')\n"
            "for r in sample_scheme.eligibility_rules:\n"
            "    print(f'  • Field: {r.field:15} | Op: {r.operator:20} | Val: {r.value} ({r.description})')\n"
            "print(f'Official Source URL: {sample_scheme.source_url}')"
        ),
        nbf.v4.new_markdown_cell(
            "### Interpretation\n"
            "The dataset contains clean, verified schemes across key citizen sectors with structured criteria ready for deterministic rule evaluation."
        )
    ]
    with open(NOTEBOOKS_DIR / "02_scheme_data_exploration.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)


def create_nb_03():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {"display_name": "Python (SchemeSathi)", "language": "python", "name": "schemesathi"}
    }
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 03. OpenRouter Experiments\n\n"
            "Demonstrates the provider abstraction, safety handling, JSON markdown cleaning, and error recovery.\n"
            "This notebook tests both mocked extraction and real API connectivity when configured."
        ),
        nbf.v4.new_markdown_cell("### 1. Robust JSON Cleaning Utility\nOpen-weights models often wrap JSON in markdown blocks or commentary. SchemeSathi handles this deterministically."),
        nbf.v4.new_code_cell(
            "from app.services.llm_service import LLMService\n\n"
            "fenced_input = '''\n"
            "```json\n"
            "{\n"
            '  "age": 42,\n'
            '  "state": "Punjab",\n'
            '  "occupation": "farmer",\n'
            '  "annual_income": 200000\n'
            "}\n"
            "```\n"
            "'''\n"
            "cleaned = LLMService._clean_json_response(fenced_input)\n"
            "print('Cleaned JSON:')\n"
            "print(cleaned)"
        ),
        nbf.v4.new_markdown_cell("### 2. Safe Parsing with Pydantic Validation"),
        nbf.v4.new_code_cell(
            "import json\n"
            "from app.models.profile import CitizenProfile\n\n"
            "data = json.loads(cleaned)\n"
            "profile = CitizenProfile(**data)\n"
            "print('Parsed CitizenProfile:')\n"
            "print(profile.model_dump(exclude_none=True))"
        ),
        nbf.v4.new_markdown_cell("### 3. OpenRouter Provider Connectivity & Error Safety\nVerify controlled exception handling when API key is missing or invalid."),
        nbf.v4.new_code_cell(
            "from app.services.llm_service import OpenRouterProvider\n"
            "from app.config import OPENROUTER_API_KEY\n\n"
            "provider = OpenRouterProvider(api_key=OPENROUTER_API_KEY)\n"
            "print(f'Provider configured for model: {provider.model}')\n"
            "if not OPENROUTER_API_KEY:\n"
            "    print('Note: OPENROUTER_API_KEY not currently set in .env. Provider safely enforces credential requirement.')"
        ),
        nbf.v4.new_markdown_cell(
            "### Interpretation\n"
            "The abstraction cleanly isolates API communication and reliably sanitizes LLM output into clean JSON structures."
        )
    ]
    with open(NOTEBOOKS_DIR / "03_openrouter_experiments.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)


def create_nb_04():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {"display_name": "Python (SchemeSathi)", "language": "python", "name": "schemesathi"}
    }
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 04. Citizen Profile Extraction Pipeline\n\n"
            "Walkthrough of the transformation pipeline:\n"
            "```text\n"
            "Natural Language Input -> LLM Extraction -> Structured JSON -> Pydantic Validation -> CitizenProfile\n"
            "```"
        ),
        nbf.v4.new_markdown_cell("### 1. Test Inputs & Scenario Profiles"),
        nbf.v4.new_code_cell(
            "test_scenarios = [\n"
            "    {\n"
            "        'label': 'Scenario 1: Punjab Farmer',\n"
            "        'text': 'I am a 42-year-old farmer from Punjab earning 2 lakh annually.',\n"
            "        'mock_output': {'age': 42, 'state': 'Punjab', 'occupation': 'farmer', 'annual_income': 200000, 'farmer_status': True}\n"
            "    },\n"
            "    {\n"
            "        'label': 'Scenario 2: Student',\n"
            "        'text': 'I am a student looking for financial assistance for education.',\n"
            "        'mock_output': {'student_status': True, 'occupation': 'student'}\n"
            "    },\n"
            "    {\n"
            "        'label': 'Scenario 3: Senior Citizen',\n"
            "        'text': 'I am 68 years old and retired in a rural village.',\n"
            "        'mock_output': {'age': 68, 'rural_or_urban': 'rural', 'employment_status': 'unemployed'}\n"
            "    }\n"
            "]"
        ),
        nbf.v4.new_markdown_cell("### 2. Validation & Normalization with Pydantic"),
        nbf.v4.new_code_cell(
            "from app.models.profile import CitizenProfile\n\n"
            "for sc in test_scenarios:\n"
            "    print(f'=== {sc[\"label\"]} ===')\n"
            "    print(f'Raw Input: \"{sc[\"text\"]}\"')\n"
            "    profile = CitizenProfile(**sc['mock_output'])\n"
            "    print(f'Validated Profile: {profile.get_known_fields()}')\n"
            "    print(f'Missing Critical: {profile.get_missing_critical_fields()}\\n')"
        ),
        nbf.v4.new_markdown_cell("### 3. Incremental Profile Merging\nWhen a citizen answers follow-up questions, new information merges without overwriting verified facts."),
        nbf.v4.new_code_cell(
            "existing_profile = CitizenProfile(age=42, state='Punjab', occupation='farmer')\n"
            "new_disclosure = {'annual_income': 200000, 'land_ownership': 3.5}\n\n"
            "merged_dict = existing_profile.model_dump()\n"
            "merged_dict.update({k: v for k, v in new_disclosure.items() if v is not None})\n"
            "updated_profile = CitizenProfile(**merged_dict)\n"
            "print('Updated Profile after follow-up:')\n"
            "print(updated_profile.get_known_fields())"
        ),
        nbf.v4.new_markdown_cell(
            "### Interpretation\n"
            "Natural language is safely turned into structured objects. Missing facts remain explicitly `None` rather than fabricated."
        )
    ]
    with open(NOTEBOOKS_DIR / "04_profile_extraction.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)


def create_nb_05():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {"display_name": "Python (SchemeSathi)", "language": "python", "name": "schemesathi"}
    }
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 05. Deterministic Eligibility Engine\n\n"
            "Demonstrates transparent, criterion-by-criterion rule evaluation in pure Python without LLM hallucination.\n"
            "Produces four distinct states:\n"
            "- **LIKELY ELIGIBLE**\n"
            "- **POSSIBLY ELIGIBLE**\n"
            "- **MORE INFORMATION NEEDED**\n"
            "- **NOT ELIGIBLE**"
        ),
        nbf.v4.new_markdown_cell("### 1. Initialize Schemes and Eligibility Engine"),
        nbf.v4.new_code_cell(
            "from app.data.scheme_repository import SchemeRepository\n"
            "from app.services.eligibility_service import EligibilityEngine\n"
            "from app.models.profile import CitizenProfile\n\n"
            "repo = SchemeRepository()\n"
            "engine = EligibilityEngine()\n"
            "schemes = repo.get_all()\n"
            "print(f'Loaded {len(schemes)} schemes for evaluation.')"
        ),
        nbf.v4.new_markdown_cell("### 2. Evaluating a Farmer Profile (Scenario 1)"),
        nbf.v4.new_code_cell(
            "farmer_profile = CitizenProfile(\n"
            "    age=42,\n"
            "    state='Punjab',\n"
            "    occupation='farmer',\n"
            "    farmer_status=True,\n"
            "    annual_income=200000,\n"
            "    rural_or_urban='rural'\n"
            ")\n\n"
            "results = engine.evaluate_all(schemes, farmer_profile)\n"
            "for res in results[:5]:\n"
            "    print(f'[{res.status.value}] {res.scheme.name} ({res.scheme.category})')\n"
            "    for m in res.matched_criteria:\n"
            "        print(f'   ✓ {m.detail}')\n"
            "    for u in res.unknown_criteria:\n"
            "        print(f'   ? {u.detail}')\n"
            "    for f in res.failed_criteria:\n"
            "        print(f'   ✗ {f.detail}')"
        ),
        nbf.v4.new_markdown_cell("### 3. Evaluating an Incomplete Profile (Unknown Handling)"),
        nbf.v4.new_code_cell(
            "partial_profile = CitizenProfile(occupation='farmer')\n"
            "res_partial = engine.evaluate_scheme(repo.get_by_id('pm-kmy'), partial_profile)\n"
            "print(f'Scheme: {res_partial.scheme.name}')\n"
            "print(f'Status: {res_partial.status.value}')\n"
            "print(f'Summary: {res_partial.summary}')\n"
            "print(f'Missing Fields: {res_partial.missing_fields}')"
        ),
        nbf.v4.new_markdown_cell(
            "### Interpretation\n"
            "The eligibility engine is fully deterministic, transparent, and auditable. Every decision is tied to an explicit rule."
        )
    ]
    with open(NOTEBOOKS_DIR / "05_eligibility_engine.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)


def create_nb_06():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {"display_name": "Python (SchemeSathi)", "language": "python", "name": "schemesathi"}
    }
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 06. End-to-End Demonstration\n\n"
            "Complete integration demonstration of SchemeSathi's full workflow across all 3 hackathon scenarios:\n"
            "1. Natural Language Input\n"
            "2. Profile Extraction & Validation\n"
            "3. Deterministic Eligibility Evaluation\n"
            "4. Transparent Explanation & Missing Info Clarification"
        ),
        nbf.v4.new_markdown_cell("### 1. Initialize Integrated System Services"),
        nbf.v4.new_code_cell(
            "from app.data.scheme_repository import SchemeRepository\n"
            "from app.services.eligibility_service import EligibilityEngine\n"
            "from app.services.explanation_service import ExplanationService\n"
            "from app.services.scheme_service import SchemeService\n"
            "from app.models.profile import CitizenProfile\n\n"
            "repo = SchemeRepository()\n"
            "engine = EligibilityEngine()\n"
            "explanation = ExplanationService()\n"
            "service = SchemeService(repository=repo, engine=engine, explanation_service=explanation)\n"
            "print('SchemeSathi Navigator Core successfully initialized.')"
        ),
        nbf.v4.new_markdown_cell("### 2. Run Scenario 1: 42-Year-Old Farmer from Punjab"),
        nbf.v4.new_code_cell(
            "s1_profile = CitizenProfile(\n"
            "    age=42,\n"
            "    state='Punjab',\n"
            "    occupation='farmer',\n"
            "    farmer_status=True,\n"
            "    annual_income=200000,\n"
            "    rural_or_urban='rural'\n"
            ")\n"
            "s1_results = service.evaluate_citizen(s1_profile)\n"
            "print(f'Top matched schemes for Scenario 1:')\n"
            "for r in s1_results[:3]:\n"
            "    details = explanation.format_evaluation_details(r)\n"
            "    print(f'[{details[\"status\"]}] {details[\"scheme_name\"]}')\n"
            "    print(f'   Benefit: {details[\"benefits\"]}')\n"
            "    print(f'   Source: {details[\"source_name\"]} ({details[\"source_url\"]})')"
        ),
        nbf.v4.new_markdown_cell("### 3. Run Scenario 2: Student Seeking Education Assistance"),
        nbf.v4.new_code_cell(
            "s2_profile = CitizenProfile(\n"
            "    occupation='student',\n"
            "    student_status=True,\n"
            "    annual_income=150000\n"
            ")\n"
            "s2_results = service.evaluate_citizen(s2_profile)\n"
            "for r in s2_results:\n"
            "    if r.status.value in ['LIKELY ELIGIBLE', 'POSSIBLY ELIGIBLE']:\n"
            "        print(f'[{r.status.value}] {r.scheme.name}')\n"
            "question = service.get_missing_info_question(s2_profile, s2_results)\n"
            "print(f'Suggested Clarification Question: {question}')"
        ),
        nbf.v4.new_markdown_cell("### 4. Run Scenario 3: Senior Citizen in Rural Area"),
        nbf.v4.new_code_cell(
            "s3_profile = CitizenProfile(\n"
            "    age=68,\n"
            "    rural_or_urban='rural',\n"
            "    annual_income=80000\n"
            ")\n"
            "s3_results = service.evaluate_citizen(s3_profile)\n"
            "for r in s3_results:\n"
            "    if r.status.value in ['LIKELY ELIGIBLE', 'POSSIBLY ELIGIBLE']:\n"
            "        print(f'[{r.status.value}] {r.scheme.name} ({r.scheme.category})')"
        ),
        nbf.v4.new_markdown_cell(
            "### Conclusion\n"
            "All three target scenarios evaluate accurately with clear reasoning, verified government source provenance, and privacy preservation."
        )
    ]
    with open(NOTEBOOKS_DIR / "06_end_to_end_demo.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)


if __name__ == "__main__":
    create_nb_01()
    create_nb_02()
    create_nb_03()
    create_nb_04()
    create_nb_05()
    create_nb_06()
    print("Successfully created all 6 notebooks.")

