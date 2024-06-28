import os
from unittest.mock import Mock, patch

import pytest
from streamlit.testing.v1 import AppTest

from modules.helpers import is_api_key_valid
from modules.youtube import (
    InvalidUrlException,
    fetch_youtube_transcript,
    get_video_metadata,
)

# def test_initial_session_state():
#    # Initialize the simulated app and execute the first script run
#    os.environ["OPENAI_API_KEY"] = "sk-proj-xyz"
#    at = AppTest("pages/summary.py", default_timeout=60.0).run()
#    assert at.session_state.model == "gpt-3.5-turbo"
#    assert at.session_state.temperature == 1.0
#    assert at.session_state.top_p == 1.0
#    assert at.session_state.save_responses is False
#    assert at.session_state.openai_api_key is not None
#
#
# def test_checking_save_responses():
#    at = AppTest("pages/summary.py", default_timeout=60.0).run()
#    assert at.session_state.save_responses is False
#    assert at.checkbox(key="save_responses").value is False
#    at.checkbox(key="save_responses").check().run()
#    assert at.session_state.save_responses is True
#    assert at.checkbox(key="save_responses").value is True


def test_invalid_video_urls():
    invalid_urls = [
        "",
        "Hello World",
        "https://platform.openai.com/docs/overview",
    ]
    for url in invalid_urls:
        with pytest.raises(InvalidUrlException):
            get_video_metadata(url)

    for url in invalid_urls:
        with pytest.raises(InvalidUrlException):
            fetch_youtube_transcript(url)


@patch("openai.models.list")
def test_valid_api_key(mock_list):
    # Mocking openai.models.list() to simulate a valid API key
    mock_list.return_value = Mock()
    result = is_api_key_valid("valid_api_key")
    assert result is True
    mock_list.assert_called_once()


def test_invalid_api_key():
    # Mocking openai.models.list() to simulate an invalid API key
    result = is_api_key_valid("invalid_api_key")
    assert result is False
