import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from modules.youtube import fetch_youtube_transcript, get_video_metadata
from modules.summary import get_completion_response
import os
import json

URL: str = "https://youtu.be/tP2sJzeqD34?si=CdpMdLgLsuytlkah"
    
def main():
    url = input("Enter URL of the YouTube Video: ")

    vid_metadata = get_video_metadata(url)

    print(f"We are working with a video called '{vid_metadata['name']}' from {vid_metadata['channel']} on {vid_metadata['provider_name']}.")
    print("I will summarize the video for you. Hang on...")
    transcript = fetch_youtube_transcript(url)
    resp = get_completion_response(transcript)
    
    # Extract the 'id' value to use as the filename
    filename = resp['id'] + '.json'
    
    # Create the directory if it does not exist
    directory = './responses'
    os.makedirs(directory, exist_ok=True)
    
    # Construct the full path for the file
    file_path = os.path.join(directory, filename)
    
    # Write the JSON response to a file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(resp, file, indent=4)


main()
