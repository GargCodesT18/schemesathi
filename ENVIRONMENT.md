# Environment Specification — SchemeSathi

## 1. Project Directory Structure
All code, models, datasets, dependencies, caches, and test artifacts are self-contained within the repository root.

---

## 2. Python Environment
- **Recommended Python Version**: `3.11`
- **Creation Command (venv)**:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  ```
- **Creation Command (Conda)**:
  ```bash
  conda create --name schemesathi python=3.11 -y
  conda activate schemesathi
  ```

---

## 3. Caches & Privacy
All temporary runtime artifacts and caches are mapped to project-local paths ignored by git:
- **Pip Cache**: `.cache/pip`
- **PyTorch Cache**: `.cache/torch`
- **HuggingFace Cache**: `.cache/huggingface`

Package installation using requirements:
```bash
pip install -r requirements.txt
```

---

## 4. Key Dependencies
- `fastapi >= 0.104.0`: High-performance REST API and static frontend mount
- `uvicorn >= 0.24.0`: ASGI web server
- `pydantic >= 2.5.0`: Strict citizen profile schema, normalizers, and validation
- `fpdf2 >= 2.7.0`: Printable Common Service Center (CSC) verification PDF docket generator
- `requests >= 2.31.0`: OpenRouter HTTP client with automated fallback
- `python-dotenv >= 1.0.0`: Secure configuration loading
- `pytest >= 7.4.0`: Offline unit and integration test suite
- `streamlit >= 1.30.0`: Streamlit minimal interface fallback

---

## 5. Jupyter Kernel Configuration
To install the Jupyter kernel for running the 6 notebooks:
```bash
python -m ipykernel install --user --name "schemesathi" --display-name "Python (SchemeSathi)"
```

To launch Jupyter:
```bash
jupyter lab
```

---

## 6. OpenRouter AI Configuration
Configure in `.env`:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

---

## 7. Execution Commands Quick Reference

| Action | Command |
|---|---|
| **Launch React + FastAPI Web App** | `uvicorn app.api:app --host 0.0.0.0 --port 8000` |
| **Launch Streamlit Web UI** | `streamlit run app/main.py` |
| **Run Test Suite (Offline)** | `pytest` |
| **Start Jupyter Notebooks** | `jupyter lab` |

