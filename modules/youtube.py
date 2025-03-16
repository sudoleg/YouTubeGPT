import json
import logging

from requests import api
from requests.exceptions import RequestException
from youtube_transcript_api import CouldNotRetrieveTranscript, YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from .helpers import extract_youtube_video_id, get_preffered_languages

OEMBED_PROVIDER = "https://noembed.com/embed"


class NoTranscriptReceivedException(Exception):
    def __init__(self, url: str):
        # message should be a user-friendly error message
        self.message = "Unfortunately, no transcript was found for this video. Therefore a summary can't be provided :slightly_frowning_face:"
        self.url = url
        super().__init__(self.message)

    def log_error(self):
        """Provides error context for developers."""
        logging.error("Could not find a transcript for %s", self.url)


class InvalidUrlException(Exception):
    def __init__(self, message: str, url: str):
        self.message = message
        self.url = url
        super().__init__(self.message)

    def log_error(self):
        """Provides error context for developers."""
        logging.error("Could not extract video_id from %s", self.url)


def get_video_metadata(url: str):
    if not ("youtube.com" in url or "youtu.be" in url):
        raise InvalidUrlException(
            "Seems not to be a YouTube URL :confused: If you are convinced that it's a YouTube URL, report the bug.",
            url,
        )

    try:
        response = api.get(OEMBED_PROVIDER, params={"url": url}, timeout=5)
    except RequestException as e:
        logging.warning("Can't retrieve metadata for provided video URL: %s", {str(e)})
        return None
    else:
        json_response = json.loads(response.text)
        return {
            "name": json_response["title"],
            "channel": json_response["author_name"],
            "provider_name": json_response["provider_name"],
        }


def fetch_youtube_transcript(url: str):
    """Fetches the transcript of a YouTube video. Returns transcript text."""

    video_id = extract_youtube_video_id(url)
    if video_id is None:
        raise InvalidUrlException(
            "Something is wrong with the URL :confused:", video_id
        )

    try:
        transcript = YouTubeTranscriptApi().fetch(
            video_id, languages=get_preffered_languages()
        )
    except CouldNotRetrieveTranscript as e:
        logging.error("Failed to retrieve transcript for URL: %s", str(e))
        raise NoTranscriptReceivedException(url)
    else:
        return TextFormatter().format_transcript(transcript)
