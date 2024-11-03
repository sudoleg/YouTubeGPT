import logging
from typing import Literal

from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
    UUIDField,
)

SQL_DB = SqliteDatabase("data/videos.sqlite3")


class BaseModel(Model):
    class Meta:
        database = SQL_DB


class Video(BaseModel):
    """Model for YouTube videos. Represents a table in a relational SQL database."""

    # id of the youtube video. not a PK but also uniquely idenfies a video
    yt_video_id = CharField(unique=True)
    title = CharField()
    link = CharField()
    channel = CharField(null=True)
    saved_on = DateTimeField(null=True)

    def chroma_collection_id(self):
        """Returns the id of the associated chroma collection."""
        transcript = Transcript.get(Transcript.video == self)
        return transcript.chroma_collection_id

    def chroma_collection_name(self):
        """Returns the name of the associated chroma collection."""
        transcript = Transcript.get(Transcript.video == self)
        return transcript.chroma_collection_name


class Transcript(BaseModel):
    """Model for transcripts of the YouTube videos. Represents a table in a relational SQL database."""

    video = ForeignKeyField(Video, backref="transcripts")
    # language of the transcript
    language = CharField(null=True)
    # whether the transcript was preprocessed
    preprocessed = BooleanField(null=True)
    # chunk size used to split the (processed) transcript
    chunk_size = IntegerField(null=True)
    # number of tokens in the original transcript
    original_token_num = IntegerField(null=True)
    # if the transcript was preprocessed, number of token in the processed transcript
    processed_token_num = IntegerField(null=True)
    # the id of the associated collection in chroma
    chroma_collection_id = UUIDField(null=True)
    # the name of the associated collection in chroma
    chroma_collection_name = CharField(null=True)


def delete_video(
    video_title: str,
):
    """Deletes the video and associated transcript from SQLite."""
    try:
        video = Video.get(Video.title == video_title)
        transcript = Transcript.select().where(Transcript.video == video)
        Transcript.delete_by_id(transcript)
        logging.info("Removed transcript for video %s from SQLite.", video.yt_video_id)
        Video.delete_by_id(video)
        logging.info("Removed video %s from SQLite.", video.yt_video_id)
    except Exception as e:
        logging.error(
            "An error occured when deleting entries from SQLite for video %s: %s",
            video.yt_video_id,
            str(e),
        )


class LibraryEntry(BaseModel):
    """Model for saved responses and summaries. Represents a table in a relational SQL database."""

    ENTRY_TYPE_CHOICES = (
        ("S", "Summary"),
        ("A", "Answer"),
    )

    entry_type = CharField(max_length=1, choices=ENTRY_TYPE_CHOICES)
    video = ForeignKeyField(Video, backref="lib_entries")
    question = TextField(null=True)
    text = TextField(null=False)


def save_library_entry(
    entry_type: Literal["S", "A"], question_text: str, response_text: str, video: Video
):
    """Saves a summary or answer entry to the library.

    Args:
        entry_type (str): Type of entry to save, "S" for summary or "A" for answer.
        question_text (str): Text of the question (used only if entry_type is "A").
        response_text (str): Text of the response or summary.
        video (Video): The video object associated with the entry.
    """
    if entry_type == "S":
        LibraryEntry.create(entry_type="S", video=video, text=response_text)
    else:
        LibraryEntry.create(
            entry_type="A", video=video, question=question_text, text=response_text
        )
    logging.info("Saved library entry for video '%s'", video.title)


def delete_library_entry(lib_entry: LibraryEntry):
    """Deletes a library entry."""
    try:
        LibraryEntry.delete_by_id(lib_entry)
    except Exception as e:
        logging.error("An error occured during the deletion of a library entry: %s", e)
    else:
        logging.info("Deleted library entry for video '%s'", lib_entry.video.title)
