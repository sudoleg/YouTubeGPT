from os import getenv

import streamlit as st

from modules.helpers import (
    get_available_models,
    get_default_config_value,
    is_api_key_set,
    is_api_key_valid,
)

GENERAL_ERROR_MESSAGE = "An unexpected error occurred. If you are a developer and run the app locally, you can view the logs to see details about the error."


def display_api_key_warning():
    """Checks whether an API key is provided and displays warning if not."""
    if not is_api_key_set():
        st.warning(
            """:warning: It seems you haven't provided an API key yet. Make sure to do so by providing it in the settings (sidebar) 
            or as an environment variable according to the [instructions](https://github.com/sudoleg/ytai?tab=readme-ov-file#installation--usage).
            Also, make sure that you have **active credit grants** and that they are not expired! You can check it [here](https://platform.openai.com/usage),
            it should be on the right side. 
            """
        )
    elif "openai_api_key" in st.session_state and not is_api_key_valid(
        st.session_state.openai_api_key
    ):
        st.warning("API key seems to be invalid.")


def set_api_key_in_session_state():
    """If the env-var OPENAI_API_KEY is set, it's value is assigned to openai_api_key property in streamlit's session state.
    Otherwise an input field for the API key is diplayed.
    """
    OPENAI_API_KEY = getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        st.sidebar.text_input(
            "Enter your OpenAI API key",
            key="openai_api_key",
            type="password",
        )
    else:
        st.session_state.openai_api_key = OPENAI_API_KEY


def is_temperature_and_top_p_altered() -> bool:
    if st.session_state.temperature != get_default_config_value(
        "temperature"
    ) and st.session_state.top_p != get_default_config_value("top_p"):
        return True
    return False


def display_model_settings_sidebar():
    """Function for displaying the sidebar and adjusting settings.

    Every widget with a key is added to streamlit's session state and can be accessed in the application.
    For example here, the selectbox for model has the key 'model'.
    Thus the selected model can be accessed via st.session_state.model.
    """
    if "model" not in st.session_state:
        st.session_state.model = get_default_config_value("default_model.gpt")

    with st.sidebar:
        st.header("Model settings")
        model = st.selectbox(
            label="Select a large language model",
            options=get_available_models(
                model_type="gpts", api_key=st.session_state.openai_api_key
            ),
            key="model",
            help=get_default_config_value("help_texts.model"),
        )
        st.slider(
            label="Adjust temperature",
            min_value=0.0,
            max_value=2.0,
            step=0.1,
            key="temperature",
            value=get_default_config_value("temperature"),
            help=get_default_config_value("help_texts.temperature"),
        )
        st.slider(
            label="Adjust Top P",
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            key="top_p",
            value=get_default_config_value("top_p"),
            help=get_default_config_value("help_texts.top_p"),
        )
        if is_temperature_and_top_p_altered():
            st.warning(
                "OpenAI generally recommends altering temperature or top_p but not both. See their [API reference](https://platform.openai.com/docs/api-reference/chat/create#chat-create-temperature)"
            )
        if model != get_default_config_value("default_model.gpt"):
            st.warning(
                """:warning: More advanced models (like gpt-4 and gpt-4o) have better reasoning capabilities and larger context windows. However, they likely won't make
                a big difference for short videos and simple tasks, like plain summarization. Also, beware of the higher costs of other [flagship models](https://platform.openai.com/docs/models/flagship-models)."""
            )


def display_link_to_repo(view: str = "main"):
    gh_link = get_default_config_value(f"github_repo_links.{view}")
    st.sidebar.write(f"[View the source code]({gh_link})")


def display_video_url_input(
    label: str = "Enter URL of the YouTube video:", disabled=False
):
    """Displays an input field for the URL of the YouTube video."""
    return st.text_input(
        label=label,
        key="url_input",
        disabled=disabled,
        help=get_default_config_value("help_texts.youtube_url"),
    )


def display_yt_video_container(video_title: str, channel: str, url: str):
    st.subheader(
        f"'{video_title}' from {channel}.",
        divider="gray",
    )
    st.video(url)


def display_nav_menu():
    """Displays links to pages in sidebar."""
    st.sidebar.page_link(page="main.py", label="Home")
    st.sidebar.page_link(page="pages/summary.py", label="Summary")
    st.sidebar.page_link(page="pages/chat.py", label="Chat")
    st.sidebar.page_link(page="pages/library.py", label="Library")


def display_download_button(data: str, file_name: str):
    st.download_button(
        label="Download",
        data=data,
        file_name=f"{file_name}.md",
        mime="text/markdown",
        icon=":material/download:",
        help="Download as markdown",
    )
