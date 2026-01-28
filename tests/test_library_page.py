"""Test library page functionality."""
from datetime import datetime as dt

import pytest
from peewee import SqliteDatabase

from modules.persistance import (
    LibraryEntry,
    Transcript,
    Video,
    get_or_create_video,
    save_library_entry,
)

# Use an in-memory database for testing
test_db = SqliteDatabase(":memory:")


@pytest.fixture
def setup_test_db():
    """Set up a test database before each test."""
    # Bind models to test database
    test_db.bind([Video, Transcript, LibraryEntry])
    test_db.connect()
    test_db.create_tables([Video, Transcript, LibraryEntry])

    yield test_db

    # Clean up after test
    test_db.drop_tables([Video, Transcript, LibraryEntry])
    test_db.close()


def test_get_summary_for_video_in_answers_tab(setup_test_db):
    """Test that we can retrieve a summary for a selected video in answers tab."""
    # Create a video
    video, _ = get_or_create_video(
        yt_video_id="test_video_123",
        link="https://www.youtube.com/watch?v=test_video_123",
        title="Test Video",
        channel="Test Channel",
        saved_on=dt.now(),
    )

    # Save a summary for the video
    save_library_entry(
        entry_type="S",
        question_text=None,
        response_text="This is a test summary of the video.",
        video=video,
    )

    # Save an answer for the video
    save_library_entry(
        entry_type="A",
        question_text="What is this video about?",
        response_text="This video is about testing.",
        video=video,
    )

    # Query for the summary (simulating what happens in the answers tab)
    saved_summary = (
        LibraryEntry.select()
        .join(Video)
        .where(
            LibraryEntry.entry_type == "S",
            Video.title == "Test Video",
        )
        .first()
    )

    # Verify the summary was found
    assert saved_summary is not None
    assert saved_summary.text == "This is a test summary of the video."
    assert saved_summary.entry_type == "S"
    assert saved_summary.video.title == "Test Video"


def test_no_summary_for_video_in_answers_tab(setup_test_db):
    """Test that when no summary exists, the query returns None."""
    # Create a video
    video, _ = get_or_create_video(
        yt_video_id="test_video_456",
        link="https://www.youtube.com/watch?v=test_video_456",
        title="Video Without Summary",
        channel="Test Channel",
        saved_on=dt.now(),
    )

    # Save only an answer (no summary)
    save_library_entry(
        entry_type="A",
        question_text="What is this video about?",
        response_text="This video is about testing.",
        video=video,
    )

    # Query for the summary (simulating what happens in the answers tab)
    saved_summary = (
        LibraryEntry.select()
        .join(Video)
        .where(
            LibraryEntry.entry_type == "S",
            Video.title == "Video Without Summary",
        )
        .first()
    )

    # Verify no summary was found
    assert saved_summary is None


def test_get_summary_for_video_in_chat_page(setup_test_db):
    """Test that we can retrieve a summary for a selected video in chat page."""
    # Create a video
    video, _ = get_or_create_video(
        yt_video_id="test_video_789",
        link="https://www.youtube.com/watch?v=test_video_789",
        title="Chat Test Video",
        channel="Test Channel",
        saved_on=dt.now(),
    )

    # Save a summary for the video
    save_library_entry(
        entry_type="S",
        question_text=None,
        response_text="This is a summary for the chat page test.",
        video=video,
    )

    # Query for the summary (simulating what happens in the chat page)
    saved_summary = (
        LibraryEntry.select()
        .where(
            LibraryEntry.entry_type == "S",
            LibraryEntry.video == video,
        )
        .first()
    )

    # Verify the summary was found
    assert saved_summary is not None
    assert saved_summary.text == "This is a summary for the chat page test."
    assert saved_summary.entry_type == "S"
    assert saved_summary.video == video


def test_no_summary_for_video_in_chat_page(setup_test_db):
    """Test that when no summary exists in chat page, the query returns None."""
    # Create a video
    video, _ = get_or_create_video(
        yt_video_id="test_video_999",
        link="https://www.youtube.com/watch?v=test_video_999",
        title="Chat Video Without Summary",
        channel="Test Channel",
        saved_on=dt.now(),
    )

    # Query for the summary (simulating what happens in the chat page)
    saved_summary = (
        LibraryEntry.select()
        .where(
            LibraryEntry.entry_type == "S",
            LibraryEntry.video == video,
        )
        .first()
    )

    # Verify no summary was found
    assert saved_summary is None
