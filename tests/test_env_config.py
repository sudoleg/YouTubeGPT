"""Tests for environment variable configuration support."""

import os


def test_provider_env_var_default(monkeypatch):
    """Test that YTGPT_LLM_PROVIDER defaults to OpenAI."""
    # Ensure env var is not set
    monkeypatch.delenv("YTGPT_LLM_PROVIDER", raising=False)

    result = os.getenv("YTGPT_LLM_PROVIDER", "OpenAI")
    assert result == "OpenAI"


def test_provider_env_var_override(monkeypatch):
    """Test that YTGPT_LLM_PROVIDER can be overridden."""
    monkeypatch.setenv("YTGPT_LLM_PROVIDER", "Ollama")
    result = os.getenv("YTGPT_LLM_PROVIDER", "OpenAI")
    assert result == "Ollama"


def test_temperature_env_var_default(monkeypatch):
    """Test that YTGPT_TEMPERATURE defaults to 1.0."""
    monkeypatch.delenv("YTGPT_TEMPERATURE", raising=False)

    result = float(os.getenv("YTGPT_TEMPERATURE", "1.0"))
    assert result == 1.0
    assert isinstance(result, float)


def test_temperature_env_var_override(monkeypatch):
    """Test that YTGPT_TEMPERATURE can be overridden."""
    monkeypatch.setenv("YTGPT_TEMPERATURE", "0.7")
    result = float(os.getenv("YTGPT_TEMPERATURE", "1.0"))
    assert result == 0.7
    assert isinstance(result, float)


def test_top_p_env_var_default(monkeypatch):
    """Test that YTGPT_TOP_P defaults to 1.0."""
    monkeypatch.delenv("YTGPT_TOP_P", raising=False)

    result = float(os.getenv("YTGPT_TOP_P", "1.0"))
    assert result == 1.0
    assert isinstance(result, float)


def test_top_p_env_var_override(monkeypatch):
    """Test that YTGPT_TOP_P can be overridden."""
    monkeypatch.setenv("YTGPT_TOP_P", "0.9")
    result = float(os.getenv("YTGPT_TOP_P", "1.0"))
    assert result == 0.9
    assert isinstance(result, float)


def test_all_env_vars_together(monkeypatch):
    """Test that all environment variables work together."""
    monkeypatch.setenv("YTGPT_LLM_PROVIDER", "Ollama")
    monkeypatch.setenv("YTGPT_TEMPERATURE", "0.5")
    monkeypatch.setenv("YTGPT_TOP_P", "0.8")

    assert os.getenv("YTGPT_LLM_PROVIDER", "OpenAI") == "Ollama"
    assert float(os.getenv("YTGPT_TEMPERATURE", "1.0")) == 0.5
    assert float(os.getenv("YTGPT_TOP_P", "1.0")) == 0.8


def test_openai_base_url_default(monkeypatch):
    """Test that OPENAI_BASE_URL defaults to the public OpenAI API."""
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)

    result = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    assert result == "https://api.openai.com/v1"


def test_openai_base_url_override(monkeypatch):
    """Test that OPENAI_BASE_URL can be overridden."""
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.com/v1")

    result = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    assert result == "https://example.com/v1"
