import os

import pytest
from langchain_openai import ChatOpenAI
from streamlit.testing.v1 import AppTest

from modules.helpers import is_api_key_valid
from modules.summary import (
    CONTEXT_WINDOWS,
    TranscriptTooLongForModelException,
    get_transcript_summary,
)
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


def test_invalid_api_key():
    # Mocking openai.models.list() to simulate an invalid API key
    result = is_api_key_valid("invalid_api_key")
    assert result is False


@pytest.fixture
def mock_llm():
    # Mock ChatOpenAI instance with the model name
    return ChatOpenAI()


def test_transcript_too_long_exception(mock_llm):
    # Create a transcript that exceeds the context window
    transcript = "word " * CONTEXT_WINDOWS["gpt-3.5-turbo"]["total"]

    with pytest.raises(
        expected_exception=TranscriptTooLongForModelException,
        match="Your transcript exceeds the context window of the chosen model",
    ) as exc_info:
        get_transcript_summary(transcript_text=transcript, llm=mock_llm)
