import json
import logging
from os import getenv

import streamlit as st
from langchain_community.callbacks import openai_info
from langchain_openai import ChatOpenAI

from modules.helpers import save_response_as_file
from modules.summary import get_transcript_summary
from modules.youtube import (
    NoTranscriptFoundException,
    fetch_youtube_transcript,
    get_video_metadata,
)

OPENAI_API_KEY = getenv("OPENAI_API_KEY")
PATH_TO_CONFIG = getenv("CONFIG_PATH", "./config.json")


def get_default_config_value(key_path: str) -> str:
    """
    Retrieves a configuration value from a JSON file using a specified key path.

    Args:
        key_path (str): A string representing the path to the desired value within the nested JSON structure,
                        with each level separated by a '.' (e.g., "level1.level2.key").

    Returns:
        The value corresponding to the key path within the configuration file. If the key path does not exist,
        a KeyError is raised.

    Raises:
        KeyError: If the specified key path is not found in the configuration.
    """
    with open(PATH_TO_CONFIG, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

        keys = key_path.split(".")
        value = config
        for key in keys:
            value = value[key]  # Navigate through each level

        return value


def get_available_models() -> tuple[str]:
    with open(PATH_TO_CONFIG, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
        models = config["available_models"]
        return tuple(models)


def display_error_message(message: str):
    st.error(message)


def display_sidebar():
    with st.sidebar:
        model = st.selectbox(
            "Select a model",
            get_available_models(),
            key="model",
            help=get_default_config_value("help_texts.model"),
        )
        temperature = st.slider(
            label="Adjust temperature",
            value=get_default_config_value("temperature"),
            min_value=0.0,
            max_value=2.0,
            step=0.1,
            key="temperature",
            help=get_default_config_value("help_texts.temperature"),
        )


def main():
    display_sidebar()

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
                llm = ChatOpenAI(
                    api_key=OPENAI_API_KEY,
                    temperature=st.session_state.temperature,
                    model=st.session_state.model,
                )
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
                    f"The transcript has {transcript_num_token} tokens. Estimated cost: {openai_info.get_openai_token_cost_for_model(model_name=st.session_state.model, num_tokens=transcript_num_token)}$"
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
