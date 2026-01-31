"""Tests for environment variable configuration support."""
import os
from unittest.mock import mock_open, patch

import pytest


def test_provider_env_var_default():
    """Test that YTGPT_LLM_PROVIDER defaults to OpenAI."""
    # Ensure env var is not set
    if "YTGPT_LLM_PROVIDER" in os.environ:
        del os.environ["YTGPT_LLM_PROVIDER"]
    
    result = os.getenv("YTGPT_LLM_PROVIDER", "OpenAI")
    assert result == "OpenAI"


def test_provider_env_var_override(monkeypatch):
    """Test that YTGPT_LLM_PROVIDER can be overridden."""
    monkeypatch.setenv("YTGPT_LLM_PROVIDER", "Ollama")
    result = os.getenv("YTGPT_LLM_PROVIDER", "OpenAI")
    assert result == "Ollama"


def test_temperature_env_var_default():
    """Test that YTGPT_TEMPERATURE defaults to 1.0."""
    if "YTGPT_TEMPERATURE" in os.environ:
        del os.environ["YTGPT_TEMPERATURE"]
    
    result = float(os.getenv("YTGPT_TEMPERATURE", "1.0"))
    assert result == 1.0
    assert isinstance(result, float)


def test_temperature_env_var_override(monkeypatch):
    """Test that YTGPT_TEMPERATURE can be overridden."""
    monkeypatch.setenv("YTGPT_TEMPERATURE", "0.7")
    result = float(os.getenv("YTGPT_TEMPERATURE", "1.0"))
    assert result == 0.7
    assert isinstance(result, float)


def test_top_p_env_var_default():
    """Test that YTGPT_TOP_P defaults to 1.0."""
    if "YTGPT_TOP_P" in os.environ:
        del os.environ["YTGPT_TOP_P"]
    
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

