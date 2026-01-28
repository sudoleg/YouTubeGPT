import whisper
import os
from modules.youtube import get_video_metadata
from pytubefix import YouTube


# Lazy load whisper model to avoid network issues at import time
# Note: This uses a simple global variable pattern which is safe for
# single-threaded Streamlit apps but not thread-safe for concurrent use
model = None

def get_whisper_model():
    """Lazy-load the Whisper model on first use.
    
    Returns the singleton Whisper model instance.
    """
    global model
    if model is None:
        model = whisper.load_model("base")
    return model


def download_mp3(video_id: str, download_folder_path: str):
    """Downloads the audio of a YouTube video and saves it as an MP3-file at the specified location.

    Returns the full path to the MP3 audio file.
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    audio_filename = get_video_metadata(video_url)["name"]
    audio_filepath = os.path.join(download_folder_path, audio_filename)
    yt = YouTube(url=video_url)
    return yt.streams.get_audio_only().download(mp3=True, filename=audio_filepath)


def generate_transcript(file_path: str):
    """Transcribes the audio file at the given path using Whisper base model.

    Returns the transcription as plain text.
    """
    transcription = get_whisper_model().transcribe(file_path)
    return transcription["text"]
