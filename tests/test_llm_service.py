"""Unit tests for LLMService and OpenRouterProvider (Offline / Mocked)"""
import pytest
from unittest.mock import MagicMock
from app.services.llm_service import LLMService, OpenRouterProvider


def test_missing_api_key_raises_value_error():
    provider = OpenRouterProvider(api_key="")
    with pytest.raises(ValueError, match="OpenRouter API key is missing"):
        provider.call_chat_completion([{"role": "user", "content": "hi"}])


def test_clean_json_response_with_markdown_fence():
    fenced = '```json\n{"age": 42, "state": "Punjab"}\n```'
    cleaned = LLMService._clean_json_response(fenced)
    assert cleaned == '{"age": 42, "state": "Punjab"}'


def test_clean_json_response_with_raw_text():
    raw = 'Here is the data: {"age": 25, "occupation": "student"} Hope this helps!'
    cleaned = LLMService._clean_json_response(raw)
    assert cleaned == '{"age": 25, "occupation": "student"}'


def test_extract_profile_successful_mock():
    mock_provider = MagicMock(spec=OpenRouterProvider)
    mock_provider.call_chat_completion.return_value = '{"age": 42, "state": "Punjab", "occupation": "farmer", "annual_income": 200000}'
    
    service = LLMService(provider=mock_provider)
    profile_data = service.extract_profile("I am a 42 year old farmer from Punjab earning 2 lakh")
    
    assert profile_data["age"] == 42
    assert profile_data["state"] == "Punjab"
    assert profile_data["occupation"] == "farmer"
    assert profile_data["annual_income"] == 200000
    mock_provider.call_chat_completion.assert_called_once()


def test_extract_profile_retry_on_malformed_json():
    mock_provider = MagicMock(spec=OpenRouterProvider)
    # First call returns malformed string, second call returns valid JSON
    mock_provider.call_chat_completion.side_effect = [
        "Not a JSON response at all",
        '{"age": 65, "occupation": "retired"}'
    ]
    
    service = LLMService(provider=mock_provider)
    profile_data = service.extract_profile("I am 65 and retired", retry_count=1)
    
    assert profile_data["age"] == 65
    assert profile_data["occupation"] == "retired"
    assert mock_provider.call_chat_completion.call_count == 2


def test_extract_profile_empty_input():
    mock_provider = MagicMock(spec=OpenRouterProvider)
    service = LLMService(provider=mock_provider)
    result = service.extract_profile("")
    assert result == {}
    mock_provider.call_chat_completion.assert_not_called()

