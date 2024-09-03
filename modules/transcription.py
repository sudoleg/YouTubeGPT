import whisper
import os
from modules.youtube import get_video_metadata
from pytubefix import YouTube


model = whisper.load_model("base")


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
    transcription = model.transcribe(file_path)
    return transcription["text"]
