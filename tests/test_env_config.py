"""Tests for environment variable configuration support."""
import os
from unittest.mock import mock_open, patch

import pytest

from modules import helpers


@pytest.fixture
def sample_config():
    """Sample config.json content."""
    return """{
    "llm_provider": "OpenAI",
    "default_model": {
        "embeddings": "text-embedding-3-small",
        "gpt": "gpt-4.1-nano"
    },
    "temperature": 1.0,
    "top_p": 1.0
}"""


def test_get_default_config_value_from_file(sample_config):
    """Test that config values are read from file when no env var is set."""
    with patch("builtins.open", mock_open(read_data=sample_config)):
        assert helpers.get_default_config_value("llm_provider") == "OpenAI"
        assert helpers.get_default_config_value("default_model.gpt") == "gpt-4.1-nano"
        assert helpers.get_default_config_value("temperature") == 1.0
        assert helpers.get_default_config_value("top_p") == 1.0


def test_get_default_config_value_from_env_provider(sample_config, monkeypatch):
    """Test that YTGPT_LLM_PROVIDER env var overrides config.json."""
    monkeypatch.setenv("YTGPT_LLM_PROVIDER", "Ollama")
    with patch("builtins.open", mock_open(read_data=sample_config)):
        assert helpers.get_default_config_value("llm_provider") == "Ollama"


def test_get_default_config_value_from_env_gpt_model(sample_config, monkeypatch):
    """Test that YTGPT_DEFAULT_GPT_MODEL env var overrides config.json."""
    monkeypatch.setenv("YTGPT_DEFAULT_GPT_MODEL", "gpt-4o")
    with patch("builtins.open", mock_open(read_data=sample_config)):
        assert helpers.get_default_config_value("default_model.gpt") == "gpt-4o"


def test_get_default_config_value_from_env_embeddings_model(sample_config, monkeypatch):
    """Test that YTGPT_DEFAULT_EMBEDDINGS_MODEL env var overrides config.json."""
    monkeypatch.setenv("YTGPT_DEFAULT_EMBEDDINGS_MODEL", "text-embedding-3-large")
    with patch("builtins.open", mock_open(read_data=sample_config)):
        assert (
            helpers.get_default_config_value("default_model.embeddings")
            == "text-embedding-3-large"
        )


def test_get_default_config_value_from_env_temperature(sample_config, monkeypatch):
    """Test that YTGPT_TEMPERATURE env var overrides config.json."""
    monkeypatch.setenv("YTGPT_TEMPERATURE", "0.5")
    with patch("builtins.open", mock_open(read_data=sample_config)):
        result = helpers.get_default_config_value("temperature")
        assert result == 0.5
        assert isinstance(result, float)


def test_get_default_config_value_from_env_top_p(sample_config, monkeypatch):
    """Test that YTGPT_TOP_P env var overrides config.json."""
    monkeypatch.setenv("YTGPT_TOP_P", "0.9")
    with patch("builtins.open", mock_open(read_data=sample_config)):
        result = helpers.get_default_config_value("top_p")
        assert result == 0.9
        assert isinstance(result, float)


def test_get_default_config_value_invalid_float_fallback(
    sample_config, monkeypatch, caplog
):
    """Test that invalid float env vars fall back to config.json."""
    monkeypatch.setenv("YTGPT_TEMPERATURE", "not-a-number")
    with patch("builtins.open", mock_open(read_data=sample_config)):
        result = helpers.get_default_config_value("temperature")
        assert result == 1.0  # Falls back to config.json
        assert "Invalid value" in caplog.text


def test_get_default_config_value_env_priority(sample_config, monkeypatch):
    """Test that environment variables take precedence over config.json."""
    monkeypatch.setenv("YTGPT_LLM_PROVIDER", "Ollama")
    monkeypatch.setenv("YTGPT_DEFAULT_GPT_MODEL", "llama3")
    monkeypatch.setenv("YTGPT_TEMPERATURE", "0.7")
    monkeypatch.setenv("YTGPT_TOP_P", "0.8")

    with patch("builtins.open", mock_open(read_data=sample_config)):
        assert helpers.get_default_config_value("llm_provider") == "Ollama"
        assert helpers.get_default_config_value("default_model.gpt") == "llama3"
        assert helpers.get_default_config_value("temperature") == 0.7
        assert helpers.get_default_config_value("top_p") == 0.8
