import json
from os import getenv
import logging

import streamlit as st
from langchain_openai import ChatOpenAI

from modules.helpers import save_response_as_file
from modules.summary import get_transcript_summary
from modules.youtube import (
    fetch_youtube_transcript,
    get_video_metadata,
    NoTranscriptFoundException,
)

from langchain_community.callbacks import openai_info

OPENAI_API_KEY = getenv("OPENAI_API_KEY")
OPENAI_MODEL = getenv("OPENAI_MODEL", "gpt-3.5-turbo")
TEMPERATURE = float(getenv("MODEL_TEMPERATURE", "0.5"))


def setup():
    with open("./config.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    st.set_page_config(
        page_title=config["app_title"], initial_sidebar_state="collapsed", menu_items={}
    )


def display_error_message(message: str):
    st.error(message)


def main():
    setup()
    llm = ChatOpenAI(model_name=OPENAI_MODEL, temperature=TEMPERATURE)

    with st.form("form"):
        url = st.text_input("Enter URL of the YouTube Video:")
        custom_prompt = st.text_input("Enter a custom prompt if you want:")
        submitted = st.form_submit_button("Go!")

        if submitted:
            vid_metadata = get_video_metadata(url)
            if vid_metadata is not None:
                st.subheader(
                    f"'{vid_metadata['name']}' from {vid_metadata['channel']} on {vid_metadata['provider_name']}.",
                    divider="rainbow",
                )
            try:
                transcript = fetch_youtube_transcript(url)
                transcript_num_token = llm.get_num_tokens(transcript)

                with st.spinner("Summarizing video. Hang on..."):
                    if custom_prompt:
                        resp = get_transcript_summary(
                            transcript, llm, custom_prompt=custom_prompt
                        )
                    else:
                        resp = get_transcript_summary(transcript, llm)

                st.markdown(resp)
                st.caption(
                    f"The transcript has {transcript_num_token} tokens. Estimated cost: {openai_info.get_openai_token_cost_for_model(OPENAI_MODEL, transcript_num_token)}$"
                )
                save_response_as_file(
                    dir_name="./responses",
                    filename=f"{vid_metadata['name']}",
                    file_content=resp,
                    content_type="markdown",
                )

            except NoTranscriptFoundException:
                display_error_message(
                    "Unfortunately, there is no transcript for this video, and therefore a summary can't be provided."
                )
            except Exception as e:
                logging.error("An unexpected error occurred %s", str(e))
                # General error handling, could be network errors, JSON parsing errors, etc.
                display_error_message(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
