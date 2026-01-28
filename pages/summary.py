import logging
from datetime import datetime as dt

import streamlit as st
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from modules.helpers import (
    extract_youtube_video_id,
    get_default_config_value,
    is_api_key_set,
    is_api_key_valid,
    is_ollama_available,
)
from modules.persistance import (
    SQL_DB,
    LibraryEntry,
    Video,
    get_or_create_video,
    save_library_entry,
)
from modules.summary import TranscriptTooLongForModelException, get_transcript_summary
from modules.ui import (
    GENERAL_ERROR_MESSAGE,
    display_api_key_warning,
    display_download_button,
    display_link_to_repo,
    display_model_settings_sidebar,
    display_nav_menu,
    display_video_url_input,
    set_api_key_in_session_state,
)
from modules.youtube import (
    InvalidUrlException,
    NoTranscriptReceivedException,
    fetch_youtube_transcript,
    get_video_metadata,
)

# --- SQLite stuff ---
SQL_DB.connect(reuse_if_open=True)
# create tables if they don't already exist
SQL_DB.create_tables([Video, LibraryEntry], safe=True)
# --- end ---

st.set_page_config("Summaries", layout="wide", initial_sidebar_state="auto")
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "OpenAI"
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "video_metadata" not in st.session_state:
    st.session_state.video_metadata = None
if "video_url" not in st.session_state:
    st.session_state.video_url = ""

display_api_key_warning()

# --- part of the sidebar which doesn't require an api key ---
display_nav_menu()
set_api_key_in_session_state()
display_link_to_repo("summary")
# --- end ---


@st.dialog(title="Transcript too long", width="large")
def display_dialog(message: str):
    """
    Displays a warning dialog with the provided message.

    Args:
        message (str): The message to display in the dialog.
    """
    st.warning(message)


def save_summary_to_lib():
    """
    Wrapper func for saving summaries to the library.

    Returns:
        None
    """
    summary_text = st.session_state.get("summary", "")
    summary_url = st.session_state.get("video_url", "")
    summary_metadata = st.session_state.get("video_metadata") or {}
    if not summary_text or not summary_url or not summary_metadata:
        st.error("No summary is ready to save yet.")
        return
    try:
        saved_video, created = get_or_create_video(
            yt_video_id=extract_youtube_video_id(url=summary_url),
            link=summary_url,
            title=summary_metadata.get("name", ""),
            channel=summary_metadata.get("channel", ""),
            saved_on=dt.now(),
        )
        save_library_entry(
            entry_type="S",
            question_text=None,
            response_text=summary_text,
            video=saved_video,
        )
    except Exception as e:
        st.error("Saving failed! If you are a developer, see logs for details!")
        logging.error("Error when saving library entry: %s", e)
    else:
        st.success("Saved summary to library successfully!")


display_model_settings_sidebar()

provider = st.session_state.llm_provider
provider_is_openai = provider == "OpenAI"
ollama_ready = is_ollama_available() if not provider_is_openai else False
openai_ready = (
    is_api_key_set() and is_api_key_valid(st.session_state.openai_api_key)
    if provider_is_openai
    else False
)
provider_ready = (provider_is_openai and openai_ready) or (
    not provider_is_openai and ollama_ready
)

if provider_ready:

    # define the columns
    col1, col2 = st.columns([0.4, 0.6], gap="large")

    with col1:
        url_input = display_video_url_input()
        custom_prompt = st.text_area(
            "Enter a custom prompt if you want:",
            key="custom_prompt_input",
            help=get_default_config_value("help_texts.custom_prompt"),
        )
        summarize_button = st.button("Summarize", key="summarize_button")
        if url_input != "":
            try:
                video_metadata = get_video_metadata(url_input)
            except InvalidUrlException as e:
                st.error(e.message)
                e.log_error()
            except Exception as e:
                logging.error("An unexpected error occurred %s", str(e))
                st.error(GENERAL_ERROR_MESSAGE)
            else:
                if video_metadata:
                    st.session_state.video_metadata = video_metadata
                    st.subheader(
                        f"'{video_metadata['name']}' from {video_metadata['channel']}.",
                        divider="gray",
                    )
                st.video(url_input)

    with col2:
        if summarize_button:
            try:
                transcript = fetch_youtube_transcript(url_input)
                if provider_is_openai:
                    llm = ChatOpenAI(
                        name=st.session_state.model,
                        api_key=st.session_state.openai_api_key,
                        temperature=st.session_state.temperature,
                        model=st.session_state.model,
                        top_p=st.session_state.top_p,
                        # max_completion_tokens=4096,
                    )
                else:
                    llm = ChatOllama(
                        name=st.session_state.model,
                        model=st.session_state.model,
                        temperature=st.session_state.temperature,
                        top_p=st.session_state.top_p,
                    )
                with st.spinner("Summarizing video :gear: Hang on..."):
                    if custom_prompt:
                        resp = get_transcript_summary(
                            transcript_text=transcript,
                            llm=llm,
                            custom_prompt=custom_prompt,
                        )
                    else:
                        resp = get_transcript_summary(
                            transcript_text=transcript, llm=llm
                        )
                st.session_state.summary = resp
                st.session_state.video_metadata = video_metadata
                st.session_state.video_url = url_input
                st.markdown(st.session_state.summary)

                with st.container(horizontal=True):
                    # button for saving summary to library
                    st.button(
                        label="Save",
                        on_click=save_summary_to_lib,
                        icon=":material/save:",
                        help="Save summary to library.",
                    )
                    # button for saving summary to file
                    display_download_button(data=resp, file_name=video_metadata["name"])
            except InvalidUrlException as e:
                st.error(e.message)
                e.log_error()
            except NoTranscriptReceivedException as e:
                st.error(e.message)
                e.log_error()
            except TranscriptTooLongForModelException as e:
                display_dialog(e.message)
                e.log_error()
            except Exception as e:
                logging.error("An unexpected error occurred: %s", str(e), exc_info=True)
                st.error(GENERAL_ERROR_MESSAGE)
else:
    if provider_is_openai:
        st.warning("Please provide a valid OpenAI API key to continue.")
    else:
        st.warning(
            "Ollama server is not available. Start the server and pull a model to continue."
        )
