import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from requests import api
import json

def get_video_metadata(url: str):
    response = api.get(
        "https://noembed.com/embed",
        params={
            "url": url
        },
        timeout=15
    )
    json_response = json.loads(response.text)
    return {
        "name": json_response['title'],
        "channel": json_response['author_name'],
        "provider_name": json_response['provider_name']
    }

def fetch_youtube_transcript(url: str):
    def extract_video_id(url):
        pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    video_id = extract_video_id(url)
    if not video_id:
        return "Error: Could not extract video ID from URL."

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        transcript = formatter.format_transcript(transcript_list)
        return transcript
    except Exception as e:
        return f"Error: {str(e)}"
