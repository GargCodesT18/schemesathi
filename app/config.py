"""Application Configuration for SchemeSathi"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory: Absolute Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment file if present
load_dotenv(BASE_DIR / ".env")

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
_raw_model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct").strip()
if _raw_model == "meta-llama/llama-3.3-70b-instruct:free":
    OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct"
else:
    OPENROUTER_MODEL = _raw_model

OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()


def get_openrouter_model() -> str:
    """Dynamically reads and normalizes the active OPENROUTER_MODEL."""
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
    model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct").strip()
    if model == "meta-llama/llama-3.3-70b-instruct:free":
        return "meta-llama/llama-3.3-70b-instruct"
    return model


def get_openrouter_api_key() -> str:
    """Dynamically reads the latest OPENROUTER_API_KEY from environment or .env without stale caching."""
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
    return os.getenv("OPENROUTER_API_KEY", "").strip()

# Data Paths
DATA_DIR = BASE_DIR / "data"
SCHEMES_FILE = DATA_DIR / "schemes.json"

# Cache Directories
CACHE_DIR = BASE_DIR / ".cache"
PIP_CACHE_DIR = CACHE_DIR / "pip"
HF_CACHE_DIR = CACHE_DIR / "huggingface"
TORCH_CACHE_DIR = CACHE_DIR / "torch"

# Application Metadata
APP_NAME = "SchemeSathi"
APP_TAGLINE = "Transparent AI-Powered Government Scheme Navigator"
APP_VERSION = "0.1.0"
