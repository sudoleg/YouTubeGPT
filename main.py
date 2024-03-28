from os import getenv

from langchain_openai import ChatOpenAI

from modules.helpers import (
    save_response_as_file,
)

from modules.summary import get_transcript_summary
from modules.youtube import (
    fetch_youtube_transcript,
    get_video_metadata,
)

OPENAI_API_KEY = getenv("OPENAI_API_KEY")
OPENAI_MODEL = getenv("OPEAI_MODEL", "gpt-3.5-turbo")
TEMPERATURE = float(getenv("MODEL_TEMPERATURE", "0.2"))


def main():
    llm = ChatOpenAI(model_name=OPENAI_MODEL, temperature=TEMPERATURE)

    url = input("Enter URL of the YouTube Video: ")
    vid_metadata = get_video_metadata(url)
    print(
        f"We are working with a video called '{vid_metadata['name']}' from {vid_metadata['channel']} on {vid_metadata['provider_name']}."
    )
    custom_prompt = input("Enter a custom prompt if you want, otherwise hit 'Enter' :")
    transcript = fetch_youtube_transcript(url)
    if custom_prompt != "":
        resp = get_transcript_summary(transcript, llm, custom_prompt=custom_prompt)
    else:
        resp = get_transcript_summary(transcript, llm)

    print("Summarizing the video for you. Hang on...")

    save_response_as_file(
        dir_name="./responses", filename=f"{vid_metadata['name']}", file_content=resp
    )
    print(resp)


if __name__ == "__main__":
    main()
