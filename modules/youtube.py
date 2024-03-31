import json
import logging

from requests import api
from requests.exceptions import RequestException
from youtube_transcript_api import YouTubeTranscriptApi, Transcript
from youtube_transcript_api import CouldNotRetrieveTranscript
from youtube_transcript_api.formatters import TextFormatter

from .helpers import (
    extract_youtube_video_id,
    save_response_as_file,
    get_preffered_languages,
)


class NoTranscriptFoundException(Exception):
    pass


def get_video_metadata(url: str):
    try:
        response = api.get("https://noembed.com/embed", params={"url": url}, timeout=5)
    except RequestException as e:
        logging.warning("Can't retrieve metadata for provided video URL: %s", {str(e)})
        return None
    else:
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
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, languages=get_preffered_languages()
        )
    except CouldNotRetrieveTranscript as e:
        logging.error("Failed to retrieve transcript for URL: %s", str(e))
        raise NoTranscriptFoundException(f"No transcript found for {url}.")
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
