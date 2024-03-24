from requests import api
import json
from os import getenv
from textwrap import dedent


API_ENDPOINT = getenv("OPENAI_API_ENDPOINT", "https://api.openai.com")
OPENAI_API_KEY = getenv("OPENAI_API_KEY")

req_headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

def get_completion_response(transcript: str):
    content = dedent(f"""Summarize the provided video transcript briefly in whole sentences. Here is the transcript, delimited by ---
                    ---
                    {transcript}
                    ---
                    """)
    prompt = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant, skilled in summarizing video transcripts and answering questions based on the transcript for general public."
            },
            {
                "role": "user",
                "content": content
            }
        ]
    }

    response = api.post(
        url=f"{API_ENDPOINT}/v1/chat/completions",
        data=json.dumps(prompt),
        headers=req_headers,
        timeout=60
    )

    resp_text = json.loads(response.text)

    return resp_text