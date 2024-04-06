import json
import logging
from os import getenv

import streamlit as st
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_openai import ChatOpenAI

from modules.helpers import save_response_as_file
from modules.summary import TranscriptTooLongForModelException, get_transcript_summary
from modules.youtube import (
    InvalidUrlException,
    NoTranscriptFoundException,
    fetch_youtube_transcript,
    get_video_metadata,
)

OPENAI_API_KEY = getenv("OPENAI_API_KEY")
PATH_TO_CONFIG = getenv("CONFIG_PATH", "./config.json")
GENERAL_ERROR_MESSAGE = "An unexpected error occurred. If you are a developer, you can view the logs to see details about the error."


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


def display_warning_message(message: str):
    st.warning(message, icon=":warning:")


def display_sidebar():
    """Function for displaying the sidebar and adjusting settings.

    Every widget with a key is added to streamlits session state and can be accessed in the application.
    Here, the selectbox for model has the key 'model'.
    Thus the selected model can be accessed via st.session_state.model.
    """
    with st.sidebar:
        st.header("(Advanced) settings", divider="rainbow")
        st.selectbox(
            "Select a model",
            get_available_models(),
            key="model",
            help=get_default_config_value("help_texts.model"),
        )
        st.slider(
            label="Adjust temperature",
            min_value=0.0,
            max_value=2.0,
            step=0.1,
            key="temperature",
            help=get_default_config_value("help_texts.temperature"),
        )
        st.checkbox(
            label="Save responses",
            value=False,
            help=get_default_config_value("help_texts.saving_responses"),
            key="save_responses",
        )


def main():
    st.set_page_config(
        "Video summarizer", layout="wide", initial_sidebar_state="collapsed"
    )
    # it's recommended to explicitly set session_state vars initially
    if "model" not in st.session_state:
        st.session_state.model = get_default_config_value("default_model")
    if "temperature" not in st.session_state:
        st.session_state.temperature = get_default_config_value("temperature")
    if "save_responses" not in st.session_state:
        st.session_state.save_responses = False
    display_sidebar()

    # define the columns
    col1, col2 = st.columns([0.4, 0.6], gap="large")

    input_form = col1.form(key="input_form", border=False, clear_on_submit=True)
    with input_form:
        url = st.text_input(
            "Enter URL of the YouTube video:",
            key="url_input",
            help=get_default_config_value("help_texts.youtube_url"),
        )
        custom_prompt = st.text_area(
            "Enter a custom prompt if you want:",
            help=get_default_config_value("help_texts.custom_prompt"),
        )
        input_submitted = st.form_submit_button("Summarize!")

    vid_metadata = None

    with col1:
        if input_submitted:
            try:
                vid_metadata = get_video_metadata(url)
            except InvalidUrlException as e:
                display_error_message(e.message)
                e.log_error()
            except Exception as e:
                logging.error("An unexpected error occurred %s", str(e))
                # General error handling, could be network errors, JSON parsing errors, etc.
                display_error_message(GENERAL_ERROR_MESSAGE)
            else:
                st.subheader(
                    f"'{vid_metadata['name']}' from {vid_metadata['channel']}.",
                    divider="rainbow",
                )
                st.video(url)

    with col2:
        if input_submitted:
            try:
                transcript = fetch_youtube_transcript(url)
                cb = OpenAICallbackHandler()
                llm = ChatOpenAI(
                    api_key=OPENAI_API_KEY,
                    temperature=st.session_state.temperature,
                    model=st.session_state.model,
                    callbacks=[cb],
                )
                with st.spinner("Summarizing video :gear: Hang on..."):
                    if custom_prompt:
                        resp = get_transcript_summary(
                            transcript, llm, custom_prompt=custom_prompt
                        )
                    else:
                        resp = get_transcript_summary(transcript, llm)
                st.markdown(resp)
                st.caption(f"The estimated cost for the request is: {cb.total_cost}$")
                if st.session_state.save_responses:
                    save_response_as_file(
                        dir_name=f"./responses/{vid_metadata['channel']}",
                        filename=f"{vid_metadata['name']}",
                        file_content=resp,
                        content_type="markdown",
                    )
            except InvalidUrlException as e:
                display_error_message(e.message)
                e.log_error()
            except NoTranscriptFoundException as e:
                display_error_message(e.message)
                e.log_error()
            except TranscriptTooLongForModelException as e:
                display_warning_message(e.message)
                e.log_error()
            except Exception as e:
                logging.error("An unexpected error occurred %s", str(e))
                display_error_message(GENERAL_ERROR_MESSAGE)


if __name__ == "__main__":
    main()
