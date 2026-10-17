"""LLM Service and OpenRouter Provider for SchemeSathi"""
import json
import logging
import re
from typing import Any, Dict, Optional
import requests
from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)

logger = logging.getLogger("schemesathi.llm")

EXTRACTION_SYSTEM_PROMPT = """You are SchemeSathi's precision entity extraction engine focused on citizen scheme navigation.
Your sole job is to extract a citizen's profile from natural-language input into a structured JSON object.

LANGUAGE SUPPORT:
You natively understand citizen input in English, Punjabi (ਪੰਜਾਬੀ), Hindi (हिंदी), and transliterated roman script (e.g., Hinglish, Roman Punjabi).
Regardless of input language, normalize all keys and values into the English canonical schema specified below:
- Occupations: ਕਿਸਾਨ / किसान -> "farmer", ਵਿਦਿਆਰਥੀ / विद्यार्थी -> "student", ਦੁਕਾਨਦਾਰ / ਫੇਰੀਵਾਲਾ / दुकानदार / विक्रेता -> "vendor", etc.
- Locations: ਪੰਜਾਬ / पंजाब -> "Punjab", ਹਰਿਆਣਾ / हरियाणा -> "Haryana", etc.
- Incomes: 2 ਲੱਖ / 2 लाख / 2 lakh -> 200000; 50 ਹਜ਼ਾਰ / 50 हजार -> 50000.
- Residence: ਪੇਂਡੂ / ग्रामीण -> "rural"; ਸ਼ਹਿਰੀ / शहरी -> "urban".

RULES:
1. ONLY return a valid JSON object. No explanation, no markdown fence, no preamble, no commentary.
2. Only include fields explicitly mentioned or directly implied by the user.
3. If a field is not mentioned, its value MUST be null. NEVER hallucinate or invent missing details.
4. Extract only these keys:
   - "age": integer or null
   - "state": string (Indian state/UT in standard English Title Case) or null
   - "district": string or null
   - "gender": "female", "male", "transgender", "other", or null
   - "occupation": string or null (e.g. "farmer", "student", "vendor", "teacher", "artisan")
   - "annual_income": number in INR or null (e.g., 200000, 300000)
   - "category": "General", "OBC", "SC", "ST", "EWS", or null
   - "rural_or_urban": "rural", "urban", or null
   - "disability_status": boolean or null
   - "student_status": boolean or null
   - "employment_status": "employed", "unemployed", "self-employed", or null
   - "farmer_status": boolean or null (true if person cultivates land or identifies as farmer)
   - "land_ownership": number of acres/hectares or null
   - "marital_status": "single", "married", "widowed", "divorced", or null
   - "children_count": integer or null

Example 1 (English): "I'm a 42-year-old farmer from Punjab with an annual family income of ₹2 lakh."
Output: {"age": 42, "state": "Punjab", "district": null, "gender": null, "occupation": "farmer", "annual_income": 200000, "category": null, "rural_or_urban": null, "disability_status": null, "student_status": false, "employment_status": "self-employed", "farmer_status": true, "land_ownership": null, "marital_status": null, "children_count": null}

Example 2 (Punjabi): "ਮੈਂ ਪੰਜਾਬ ਤੋਂ 42 ਸਾਲਾਂ ਦਾ ਕਿਸਾਨ ਹਾਂ ਅਤੇ ਮੇਰੀ ਸਾਲਾਨਾ ਪਰਿਵਾਰਕ ਆਮਦਨ 2 ਲੱਖ ਰੁਪਏ ਹੈ।"
Output: {"age": 42, "state": "Punjab", "district": null, "gender": null, "occupation": "farmer", "annual_income": 200000, "category": null, "rural_or_urban": null, "disability_status": null, "student_status": false, "employment_status": "self-employed", "farmer_status": true, "land_ownership": null, "marital_status": null, "children_count": null}

Example 3 (Hindi): "मैं पंजाब से 42 साल का किसान हूँ, पारिवारिक वार्षिक आय 2 लाख रुपये है।"
Output: {"age": 42, "state": "Punjab", "district": null, "gender": null, "occupation": "farmer", "annual_income": 200000, "category": null, "rural_or_urban": null, "disability_status": null, "student_status": false, "employment_status": "self-employed", "farmer_status": true, "land_ownership": null, "marital_status": null, "children_count": null}

Example 4 (Roman Punjabi / Hinglish): "Main Punjab toh 42 saal da kisan han te meri salana aamdani 2 lakh rupaye hai."
Output: {"age": 42, "state": "Punjab", "district": null, "gender": null, "occupation": "farmer", "annual_income": 200000, "category": null, "rural_or_urban": null, "disability_status": null, "student_status": false, "employment_status": "self-employed", "farmer_status": true, "land_ownership": null, "marital_status": null, "children_count": null}
"""


class OpenRouterProvider:
    """Handles communication with OpenRouter API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        if api_key is not None:
            self.api_key = api_key.strip()
        else:
            from app.config import get_openrouter_api_key
            self.api_key = get_openrouter_api_key()

        raw_model = model or OPENROUTER_MODEL
        if raw_model == "meta-llama/llama-3.3-70b-instruct:free":
            self.model = "meta-llama/llama-3.3-70b-instruct"
        else:
            self.model = raw_model

        self.base_url = (base_url or OPENROUTER_BASE_URL).rstrip("/")
        self.timeout = timeout

    def call_chat_completion(self, messages: list[dict], temperature: float = 0.0) -> str:
        """Sends chat request to OpenRouter endpoint with automated fallback."""
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is missing. Please set OPENROUTER_API_KEY in .env or provide it via the UI sidebar."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/schemesathi",
            "X-Title": "SchemeSathi Navigator",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/chat/completions"
        
        # Build candidate models list to handle OpenRouter dynamic model availability
        candidate_models = []
        if self.model:
            candidate_models.append(self.model)
            if ":free" in self.model:
                candidate_models.append(self.model.replace(":free", ""))

        for m in [
            "meta-llama/llama-3.3-70b-instruct",
            "meta-llama/llama-3.1-8b-instruct",
            "google/gemini-2.0-flash-exp:free",
            "mistralai/mistral-7b-instruct:free"
        ]:
            if m not in candidate_models:
                candidate_models.append(m)

        last_error = None
        for candidate in candidate_models:
            payload = {
                "model": candidate,
                "messages": messages,
                "temperature": temperature,
            }
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
                if resp.status_code == 404:
                    logger.warning(f"Model {candidate} unavailable (404), trying next candidate...")
                    continue
                resp.raise_for_status()
                data = resp.json()
                self.model = candidate  # Remember working model
                return data["choices"][0]["message"]["content"]
            except requests.exceptions.Timeout:
                last_error = TimeoutError("Request to OpenRouter timed out. Please check your network or try again.")
            except requests.exceptions.HTTPError:
                status_code = resp.status_code if resp is not None else 0
                if status_code == 401:
                    raise PermissionError("Invalid OpenRouter API Key. Please verify your credentials.")
                elif status_code == 429:
                    raise RuntimeError("OpenRouter rate limit reached. Please wait a moment before trying again.")
                elif status_code == 404:
                    continue
                else:
                    last_error = RuntimeError(f"OpenRouter API error ({status_code}): {resp.text}")
            except Exception as e:
                last_error = RuntimeError(f"Unexpected error communicating with OpenRouter: {str(e)}")

        if last_error:
            raise last_error


class LLMService:
    """Provider-agnostic LLM interface for SchemeSathi.
    
    Provides language understanding and profile extraction while decoupling
    the underlying model provider (OpenRouter currently, local inference in future).
    """

    def __init__(self, provider: Optional[OpenRouterProvider] = None):
        self.provider = provider or OpenRouterProvider()

    @staticmethod
    def _clean_json_response(raw_text: str) -> str:
        """Extracts JSON substring from LLM response even if wrapped in markdown codeblocks."""
        text = raw_text.strip()
        # Check for ```json ... ``` or ``` ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            return match.group(1).strip()
        
        # If brackets present, find outermost curly brace
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start:end + 1]
        
        return text

    def extract_profile(self, user_message: str, retry_count: int = 1) -> Dict[str, Any]:
        """Extracts citizen profile attributes from natural language.
        
        Attempts clean parsing, with up to `retry_count` fallback attempts.
        """
        if not user_message or not user_message.strip():
            return {}

        messages = [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_message.strip()},
        ]

        last_error = None
        for attempt in range(retry_count + 1):
            try:
                raw_response = self.provider.call_chat_completion(messages, temperature=0.0)
                cleaned_json = self._clean_json_response(raw_response)
                parsed = json.loads(cleaned_json)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    raise ValueError(f"Extracted content is not a dictionary: {parsed}")
            except (json.JSONDecodeError, ValueError) as err:
                last_error = err
                if attempt < retry_count:
                    # Provide feedback on retry
                    messages.append({"role": "assistant", "content": raw_response if 'raw_response' in locals() else ""})
                    messages.append({
                        "role": "user",
                        "content": "Your previous output was not valid JSON. Output strictly valid raw JSON only, starting with { and ending with }."
                    })
            except Exception as e:
                # Upstream network/auth errors should raise immediately
                raise e

        raise ValueError(f"Failed to extract structured profile from input after retry: {last_error}")
