import os
import tempfile
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


def test_get_or_create_video_creates_new(setup_test_db):
    """Test that get_or_create_video creates a new video when it doesn't exist."""
    yt_video_id = "test_video_123"
    link = "https://www.youtube.com/watch?v=test_video_123"
    title = "Test Video"
    channel = "Test Channel"
    saved_on = dt.now()

    video, created = get_or_create_video(
        yt_video_id=yt_video_id,
        link=link,
        title=title,
        channel=channel,
        saved_on=saved_on,
    )

    assert created is True
    assert video.yt_video_id == yt_video_id
    assert video.title == title
    assert video.link == link
    assert video.channel == channel


def test_get_or_create_video_gets_existing(setup_test_db):
    """Test that get_or_create_video returns existing video instead of creating duplicate."""
    yt_video_id = "test_video_456"
    link = "https://www.youtube.com/watch?v=test_video_456"
    title = "Test Video 2"
    channel = "Test Channel 2"
    saved_on = dt.now()

    # Create video first time
    video1, created1 = get_or_create_video(
        yt_video_id=yt_video_id,
        link=link,
        title=title,
        channel=channel,
        saved_on=saved_on,
    )

    assert created1 is True

    # Try to create same video again
    video2, created2 = get_or_create_video(
        yt_video_id=yt_video_id,
        link=link,
        title=title,
        channel=channel,
        saved_on=saved_on,
    )

    assert created2 is False
    assert video1.id == video2.id
    assert video1.yt_video_id == video2.yt_video_id


def test_save_summary_with_existing_video(setup_test_db):
    """Test that saving a summary works when video already exists."""
    yt_video_id = "test_video_789"
    link = "https://www.youtube.com/watch?v=test_video_789"
    title = "Test Video 3"
    channel = "Test Channel 3"
    saved_on = dt.now()

    # Create video first (simulating summary.py saving a video)
    video, created = get_or_create_video(
        yt_video_id=yt_video_id,
        link=link,
        title=title,
        channel=channel,
        saved_on=saved_on,
    )

    # Save a summary
    save_library_entry(
        entry_type="S",
        question_text=None,
        response_text="This is a test summary",
        video=video,
    )

    # Now try to get the same video again (simulating chat.py)
    video2, created2 = get_or_create_video(
        yt_video_id=yt_video_id,
        link=link,
        title=title,
        channel=channel,
        saved_on=saved_on,
    )

    # Should not create a new video
    assert created2 is False
    assert video.id == video2.id

    # Verify we can create a transcript for this video
    transcript = Transcript.create(
        video=video2,
        original_token_num=1000,
    )

    assert transcript.video.id == video.id
