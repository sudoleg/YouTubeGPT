import json
from os import getenv

import streamlit as st
from langchain_openai import ChatOpenAI

from modules.helpers import save_response_as_file
from modules.summary import get_transcript_summary
from modules.youtube import fetch_youtube_transcript, get_video_metadata

OPENAI_API_KEY = getenv("OPENAI_API_KEY")
OPENAI_MODEL = getenv("OPEAI_MODEL", "gpt-3.5-turbo")
TEMPERATURE = float(getenv("MODEL_TEMPERATURE", "0.5"))


def setup():
    with open("./config.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    st.set_page_config(
        page_title=config["app_title"], initial_sidebar_state="collapsed", menu_items={}
    )


def main():
    setup()
    llm = ChatOpenAI(model_name=OPENAI_MODEL, temperature=TEMPERATURE)

    with st.form("form"):
        url = st.text_input("Enter URL of the YouTube Video:")
        custom_prompt = st.text_input("Enter a custom prompt if you want:")
        submitted = st.form_submit_button("Go!")

        if submitted:
            vid_metadata = get_video_metadata(url)
            st.subheader(
                f"'{vid_metadata['name']}' from {vid_metadata['channel']} on {vid_metadata['provider_name']}.",
                divider="rainbow",
            )
            transcript = fetch_youtube_transcript(url)
            with st.spinner("Summarizing video. Hang on..."):
                if custom_prompt:
                    resp = get_transcript_summary(
                        transcript, llm, custom_prompt=custom_prompt
                    )
                else:
                    resp = get_transcript_summary(transcript, llm)
            st.markdown(resp)
            save_response_as_file(
                dir_name="./responses",
                filename=f"{vid_metadata['name']}",
                file_content=resp,
                content_type="markdown",
            )


if __name__ == "__main__":
    main()
