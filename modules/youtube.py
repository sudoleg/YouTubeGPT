import json

from requests import api
from youtube_transcript_api import YouTubeTranscriptApi, Transcript
from youtube_transcript_api import CouldNotRetrieveTranscript
from youtube_transcript_api.formatters import TextFormatter

from .helpers import extract_youtube_video_id, save_response_as_file


class NoTranscriptFoundException(Exception):
    pass


def get_video_metadata(url: str):
    response = api.get("https://noembed.com/embed", params={"url": url}, timeout=15)
    json_response = json.loads(response.text)
    save_response_as_file(
        dir_name="./video_meta",
        filename=f"{json_response['title']}",
        file_content=json_response,
        content_type="json",
    )
    return {
        "name": json_response["title"],
        "channel": json_response["author_name"],
        "provider_name": json_response["provider_name"],
    }


def fetch_youtube_transcript(url: str):
    video_id = extract_youtube_video_id(url)
    if video_id is None:
        return "Error: Could not extract video ID from URL."

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    except CouldNotRetrieveTranscript as e:
        print(f"Error: {str(e)}")
        raise NoTranscriptFoundException
    else:
        formatter = TextFormatter()
        transcript = formatter.format_transcript(transcript_list)
        return transcript


def analyze_transcripts(video_id: str):
    try:
        transcript_list: list[Transcript] = YouTubeTranscriptApi.list_transcripts(
            video_id
        )
    except Exception as e:
        print("An error occured when fetching transcripts: " + e)
        return
    else:
        for t in transcript_list:
            if t.is_generated:
                print(
                    f"found auto-generated transcript in {t.language} ({t.language_code})!"
                )
            else:
                print(f"found manual transcript in {t.language} ({t.language_code})!")
