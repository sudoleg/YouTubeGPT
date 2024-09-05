import logging

import streamlit as st

from modules.helpers import is_api_key_set, is_api_key_valid, read_file
from modules.ui import display_link_to_repo, display_nav_menu


def main():
    st.set_page_config(
        page_title="YouTube AI", layout="wide", initial_sidebar_state="auto"
    )

    # display sidebar with page links
    display_nav_menu()
    display_link_to_repo()

    if not is_api_key_set():
        st.info(
            """It looks like you haven't set the API Key as an environment variable. 
                Don't worry, you can set it in the sidebar when you go to either one of the pages :)"""
        )
    else:
        st.success("API Key set!")
        if not is_api_key_valid(st.session_state.openai_api_key):
            st.warning("It looks like you have provided an invalid API Key!")

    st.markdown(body=read_file(".assets/home.md"))


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        level=logging.INFO,
    )
    main()
