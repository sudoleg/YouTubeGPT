import logging

import chromadb
from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
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
    # the name of the associated collection in chroma
    chroma_collection_name = CharField(null=True)


def delete_video(
    video_title: str, chroma_client: chromadb.HttpClient, collection_name: str
):
    """Deletes the video and associated transcript from SQLite. Also removes the associated collection from ChromaDB."""

    video = Video.get(Video.title == video_title)
    transcript = Transcript.select().where(Transcript.video == video)
    Transcript.delete_by_id(transcript)
    logging.info("Removed transcript for video %s from SQLite.", video.yt_video_id)
    Video.delete_by_id(video)
    logging.info("Removed video %s from SQLite.", video.yt_video_id)
    chroma_client.delete_collection(collection_name)
    logging.info("Removed collection %s from ChromaDB.", collection_name)
